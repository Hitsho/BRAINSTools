#! /usr/bin/env python
"""
template.py
=========
This program is used to generate the subject- and session-specific workflows for BRAINSTool processing

Usage:
  template.py [--rewrite-datasinks] [--wfrun PLUGIN] --subject ID... --pe ENV --ExperimentConfig FILE
  template.py -v | --version
  template.py -h | --help

Arguments:


Options:
  -h, --help            Show this help and exit
  -v, --version         Print the version and exit
  --rewrite-datasinks   Turn on the Nipype option to overwrite all files in the 'results' directory
  --pe ENV              The processing environment to use from configuration file
  --subject ID          The subject ID to process
  --wfrun PLUGIN        The name of the workflow plugin option (default: 'local')
  --ExperimentConfig FILE   The configuration file

Examples:
  $ template.py --subject 1058 --pe OSX --ExperimentConfig my_baw.config
  $ template.py --wfrun helium_all.q --subject 1058 --pe OSX --ExperimentConfig my_baw.config
  $ template.py --rewrite-datasinks --subject 1058 --pe OSX --ExperimentConfig my_baw.config

"""

def modify_qsub_args(queue, memory, minThreads=1, maxThreads=None, stdout='/dev/null', stderr='/dev/null', hard=True):
    """ Outputs qsub_args string for Nipype nodes """
    if maxThreads is None:
        if hard:
            format_str = '-S /bin/bash -cwd -pe smp {mint} -l mem_free={mem} -o {stdout} -e {stderr} {queue}'
        else:
            format_str = '-S /bin/bash -cwd -pe smp {mint}- -l mem_free={mem} -o {stdout} -e {stderr} {queue}'
        return format_str.format(mint=minThreads, mem=memory, stdout=stdout, stderr=stderr, queue=queue)
    else:
        format_str = '-S /bin/bash -cwd -pe smp {mint}-{maxt} -l mem_free={mem} -o {stdout} -e {stderr} {queue}'
        return format_str.format(mint=minThreads, maxt=maxThreads, mem=memory, stdout=stdout, stderr=stderr, queue=queue)


def MergeByExtendListElements(t1s, t2s, pds, fls, labels, posteriors):
    """
    *** NOTE:  ALl input lists MUST have the same number of elements (even if they are null) ***

    output = [{'T1': os.path.join(mydatadir, '01_T1_half.nii.gz'),
                               'INV_T1': os.path.join(mydatadir, '01_T1_inv_half.nii.gz'),
                               'LABEL_MAP': os.path.join(mydatadir, '01_T1_inv_half.nii.gz')
                              },
                              {'T1': os.path.join(mydatadir, '02_T1_half.nii.gz'),
                               'INV_T1': os.path.join(mydatadir, '02_T1_inv_half.nii.gz'),
                               'LABEL_MAP': os.path.join(mydatadir, '02_T1_inv_half.nii.gz')
                              },
                              {'T1': os.path.join(mydatadir, '03_T1_half.nii.gz'),
                               'INV_T1': os.path.join(mydatadir, '03_T1_inv_half.nii.gz'),
                               'LABEL_MAP': os.path.join(mydatadir, '03_T1_inv_half.nii.gz')
                              }
                             ]
    labels = ['brain_label_seg.nii.gz', 'brain_label_seg.nii.gz']
    pds = [None, None]
    t1s = ['t1_average_BRAINSABC.nii.gz', 't1_average_BRAINSABC.nii.gz']
    t2s = ['t2_average_BRAINSABC.nii.gz', 't2_average_BRAINSABC.nii.gz']

    """
    # print "t1s", t1s
    # print "t2s", t2s
    # print "pds", pds
    # print "fls", fls
    # print "labels", labels
    # print "$$$$$$$$$$$$$$$$$$$$$$$"
    # print "posteriors", posteriors
    ListOfImagesDictionaries = [dict() for i in t1s]  # Initial list with empty dictionaries
    ## HACK:  Need to make it so that AVG_AIR.nii.gz has a background value of 1
    registrationImageTypes = ['T1']  # ['T1','T2'] someday.
    DefaultContinuousInterpolationType = 'Linear'  # or 'LanczosWindowedSinc' ('Linear' for speed)
    interpolationMapping = {'T1': DefaultContinuousInterpolationType,
                            'T2': DefaultContinuousInterpolationType,
                            'PD': DefaultContinuousInterpolationType,
                            'FL': DefaultContinuousInterpolationType,
                            'BRAINMASK': 'MultiLabel'
                            }
    for list_index in range(len(t1s)):
        if t1s[list_index] is not None:
            ListOfImagesDictionaries[list_index]['T1'] = t1s[list_index]
        if isinstance(t2s, list) and t2s[list_index] is not None:
            ListOfImagesDictionaries[list_index]['T2'] = t2s[list_index]
        if isinstance(pds, list) and pds[list_index] is not None:
            ListOfImagesDictionaries[list_index]['PD'] = pds[list_index]
        if isinstance(fls, list) and fls[list_index] is not None:
            ListOfImagesDictionaries[list_index]['FL'] = fls[list_index]
        if labels[list_index] is not None:
            ListOfImagesDictionaries[list_index]['BRAINMASK'] = labels[list_index]
        print ListOfImagesDictionaries[list_index]
        for key, value in posteriors.items():
            # print "key:", key, " -> value:", value
            ListOfImagesDictionaries[list_index][key] = value[list_index]

    # print "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
    # print "ListOfImagesDictionaries", ListOfImagesDictionaries
    # print "registrationImageTypes", registrationImageTypes
    # print "interpolationMapping", interpolationMapping
    return ListOfImagesDictionaries, registrationImageTypes, interpolationMapping


def xml_filename(subject):
    return 'AtlasDefinition_{0}.xml'.format(subject)


def template(args):
    subjects, master_config = args

    import os
    import sys
    import traceback

    # Set universal pipeline options
    from nipype import config
    config.update_config(master_config)
    assert config.get('execution', 'plugin') == master_config['execution']['plugin']

    import nipype.pipeline.engine as pe
    import nipype.interfaces.io as nio
    from nipype.interfaces.utility import IdentityInterface, Function
    import nipype.interfaces.ants as ants

    from template import MergeByExtendListElements, xml_filename, modify_qsub_args
    from PipeLineFunctionHelpers import mapPosteriorList
    from atlasNode import GetAtlasNode, MakeNewAtlasTemplate
    from utilities.misc import template_subs

    template = pe.Workflow(name='SubjectAtlas_Template')
    template.base_dir = master_config['logging']['log_directory']

    BAtlas = GetAtlasNode(master_config['previouscache'], 'BAtlas')
    Atlas_DataSink = pe.Node(nio.DataSink(), name="Atlas_DS")
    Atlas_DataSink.overwrite = master_config['ds_overwrite']
    Atlas_DataSink.inputs.base_directory = master_config['resultdir']
    Atlas_DataSink.inputs.parameterization = False

    template.connect([(BAtlas, Atlas_DataSink, [('template_landmarks_50Lmks_fcsv', 'Atlas.@fcsv'),
                                                ('template_weights_50Lmks_wts', 'Atlas.@wts'),
                                                ('LLSModel_50Lmks_hdf5', 'Atlas.@hdf5'),
                                                ('T1_50Lmks_mdl', 'Atlas.@mdl')])])

    inputspec = pe.Node(interface=IdentityInterface(fields=['subject']), name='inputspec')
    inputspec.iterables = ('subject', subjects)

    baselineDG = pe.Node(nio.DataGrabber(infields=['subject'], outfields=['t1_average', 't2_average', 'pd_average',
                                                                            'fl_average', 'outputLabels', 'posteriorImages']),
                         name='PHASE_1_DG')
    baselineDG.inputs.base_directory = master_config['previousresult']
    baselineDG.inputs.sort_filelist = True
    baselineDG.inputs.raise_on_empty = False
    baselineDG.inputs.template = '*/%s/*/Phase_1/%s.nii.gz'
    baselineDG.inputs.template_args['t1_average'] = [['subject', 't1_average_BRAINSABC']]
    baselineDG.inputs.template_args['t2_average'] = [['subject', 't2_average_BRAINSABC']]
    baselineDG.inputs.template_args['pd_average'] = [['subject', 'pd_average_BRAINSABC']]
    baselineDG.inputs.template_args['fl_average'] = [['subject', 'fl_average_BRAINSABC']]
    baselineDG.inputs.template_args['outputLabels'] = [['subject', 'brain_label_seg']]
    baselineDG.inputs.field_template = {'posteriorImages':'*/%s/*/Phase_1/TissueClassify/POSTERIOR_%s.nii.gz'}
    from utilities import posteriors
    baselineDG.inputs.template_args['posteriorImages'] = [['subject', posteriors]]

    MergeByExtendListElementsNode = pe.Node(Function(function=MergeByExtendListElements,
                                                     input_names=['t1s', 't2s',
                                                                  'pds', 'fls',
                                                                  'labels', 'posteriors'],
                                                     output_names=['ListOfImagesDictionaries', 'registrationImageTypes',
                                                                   'interpolationMapping']),
                                            run_without_submitting=True, name="99_MergeByExtendListElements")
    from PipeLineFunctionHelpers import WrapPosteriorImagesFromDictionaryFunction as wrapfunc
    template.connect([(inputspec, baselineDG, [('subject', 'subject')]),
                      (baselineDG, MergeByExtendListElementsNode, [('t1_average', 't1s'),
                                                                   ('t2_average', 't2s'),
                                                                   ('pd_average', 'pds'),
                                                                   ('fl_average', 'fls'),
                                                                   ('outputLabels', 'labels'),
                                                                   (('posteriorImages', wrapfunc), 'posteriors')])
                    ])

    myInitAvgWF = pe.Node(interface=ants.AverageImages(), name='Atlas_antsSimpleAverage')  # was 'Phase1_antsSimpleAverage'
    myInitAvgWF.inputs.dimension = 3
    myInitAvgWF.inputs.normalize = True
    template.connect(baselineDG, 't1_average', myInitAvgWF, "images")
    ####################################################################################################
    # TEMPLATE_BUILD_RUN_MODE = 'MULTI_IMAGE'
    # if numSessions == 1:
    #     TEMPLATE_BUILD_RUN_MODE = 'SINGLE_IMAGE'
    ####################################################################################################
    from BAWantsRegistrationBuildTemplate import BAWantsRegistrationTemplateBuildSingleIterationWF as registrationWF
    buildTemplateIteration1 = registrationWF('iteration01')
    # buildTemplateIteration2 = buildTemplateIteration1.clone(name='buildTemplateIteration2')
    buildTemplateIteration2 = registrationWF('Iteration02')

    MakeNewAtlasTemplateNode = pe.Node(interface=Function(function=MakeNewAtlasTemplate,
                                                          input_names=['t1_image', 'deformed_list', 'AtlasTemplate', 'outDefinition'],
                                                          output_names=['outAtlasFullPath', 'clean_deformed_list']),
                                       # This is a lot of work, so submit it run_without_submitting=True,
                                       run_without_submitting=True,  # HACK:  THIS NODE REALLY SHOULD RUN ON THE CLUSTER!
                                       name='99_MakeNewAtlasTemplate')

    if master_config['execution']['plugin'] == 'SGE':  # for some nodes, the qsub call needs to be modified on the cluster

        MakeNewAtlasTemplateNode.plugin_args = {'template': master_config['plugin_args']['template'],
                                                'qsub_args': modify_qsub_args(master_config['queue'], '1000M', 1, 1),
                                                'overwrite': True}
        for bt in [buildTemplateIteration1, buildTemplateIteration2]:
            ##################################################
            # *** Hans, is this TODO already addressed? ***  #
            # ---->  # TODO:  Change these parameters  <---- #
            ##################################################
            BeginANTS = bt.get_node("BeginANTS")
            BeginANTS.plugin_args = {'template': master_config['plugin_args']['template'], 'overwrite': True,
                                     'qsub_args': modify_qsub_args(master_config['queue'], '9000M', 4, hard=False)}
            wimtdeformed = bt.get_node("wimtdeformed")
            wimtdeformed.plugin_args = {'template': master_config['plugin_args']['template'], 'overwrite': True,
                                        'qsub_args': modify_qsub_args(master_config['queue'], '2000M', 1, 2)}
            AvgAffineTransform = bt.get_node("AvgAffineTransform")
            AvgAffineTransform.plugin_args = {'template': master_config['plugin_args']['template'], 'overwrite': True,
                                              'qsub_args': modify_qsub_args(master_config['queue'], '2000M', 1)}
            wimtPassivedeformed = bt.get_node("wimtPassivedeformed")
            wimtPassivedeformed.plugin_args = {'template': master_config['plugin_args']['template'], 'overwrite': True,
                                                'qsub_args': modify_qsub_args(master_config['queue'], '2000M', 1, 2)}

    template.connect([(myInitAvgWF, buildTemplateIteration1, [('output_average_image', 'inputspec.fixed_image')]),
                      (MergeByExtendListElementsNode, buildTemplateIteration1, [('ListOfImagesDictionaries', 'inputspec.ListOfImagesDictionaries'),
                                                                                ('registrationImageTypes', 'inputspec.registrationImageTypes'),
                                                                                ('interpolationMapping','inputspec.interpolationMapping')]),
                      (buildTemplateIteration1, buildTemplateIteration2, [('outputspec.template', 'inputspec.fixed_image')]),
                      (MergeByExtendListElementsNode, buildTemplateIteration2, [('ListOfImagesDictionaries', 'inputspec.ListOfImagesDictionaries'),
                                                                                ('registrationImageTypes','inputspec.registrationImageTypes'),
                                                                                ('interpolationMapping', 'inputspec.interpolationMapping')]),
                      (inputspec, MakeNewAtlasTemplateNode, [(('subject', xml_filename), 'outDefinition')]),
                      (BAtlas, MakeNewAtlasTemplateNode, [('ExtendedAtlasDefinition_xml_in', 'AtlasTemplate')]),
                      (buildTemplateIteration2, MakeNewAtlasTemplateNode, [('outputspec.template', 't1_image'),
                                                                           ('outputspec.passive_deformed_templates', 'deformed_list')]),
                      ])

    # Create DataSinks
    Subject_DataSink = pe.Node(nio.DataSink(), name="Subject_DS")
    Subject_DataSink.overwrite = master_config['ds_overwrite']
    Subject_DataSink.inputs.base_directory = master_config['resultdir']
    Subject_DataSink.inputs.parameterization = True
    Subject_DataSink.inputs.container = 'SUBJECT_TEMPLATES'
    Subject_DataSink.inputs.substitutions =
    Subject_DataSink.inputs.regexp_substitutions = [('CLIPPED_AVG_(?P<structure>.*.nii.gz)', 'AVG_\\g<structure>')]

    template.connect([(inputspec, Subject_DataSink, [(('subject', template_subs), 'substitutions')]),
                      (buildTemplateIteration1, Subject_DataSink, [('outputspec.template', 'template.iteration1')]),
                      (MakeNewAtlasTemplateNode, Atlas_DataSink, [('outAtlasFullPath', 'Atlas.definitions')]),
                      (buildTemplateIteration2, Subject_DataSink, [('outputspec.template', 'template')]),
                      (MakeNewAtlasTemplateNode, Subject_DataSink, [('clean_deformed_list', 'template.@passive')]),
                     ])

    if master_config['execution']['plugin'] in ['Linear', 'MultiProc']:
        try:
            print "Writing out graph!"
            graphtype = 'hierarchical'
            template.write_graph(dotfilename='subject', graph2use=graphtype)
        except:
            raise
    try:
        print "Running workflow..."
        if not master_config['execution']['plugin'] in ['Linear', 'MultiProc']:
            template.run(plugin_args=master_config['plugin_args'])
        else:
            template.run()
    except:
        print "=+-+" * 25
        print ("Error: Exception while running subjects")
        traceback.print_exc(file=sys.stdout)
        return False
    return True


if __name__ == '__main__':
    import sys
    from AutoWorkup import setup

    from docopt import docopt

    argv = docopt(__doc__, version='1.1')
    print argv
    print '=' * 100
    exit = setup(argv)
    sys.exit(exit)
