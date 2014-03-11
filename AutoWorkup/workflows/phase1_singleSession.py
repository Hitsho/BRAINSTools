#!/usr/bin/python
#################################################################################
## Program:   BRAINS (Brain Research: Analysis of Images, Networks, and Systems)
## Language:  Python
##
## Author:  Hans J. Johnson, David Welch
##
##      This software is distributed WITHOUT ANY WARRANTY; without even
##      the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
##      PURPOSE.  See the above copyright notices for more information.
##
#################################################################################

import sys
import string
#"""Import necessary modules from nipype."""
# from nipype.utils.config import config
# config.set('logging', 'log_to_file', 'false')
# config.set_log_dir(os.getcwd())
#--config.set('logging', 'workflow_level', 'DEBUG')
#--config.set('logging', 'interface_level', 'DEBUG')
#--config.set('execution','remove_unnecessary_outputs','false')

from nipype.utils.misc import package_check
# package_check('nipype', '5.4', 'tutorial1') ## HACK: Check nipype version
package_check('numpy', '1.3', 'tutorial1')
package_check('scipy', '0.7', 'tutorial1')
package_check('networkx', '1.0', 'tutorial1')
package_check('IPython', '0.10', 'tutorial1')

from SEMTools import *

def get_list_element(nestedList, index):
    return nestedList[index]

def getAllT1sLength(allT1s):
    return len(allT1s)

def sessionWorkflow(projectid, subjectid, sessionid, phase, config, interpMode='Linear', pipeline_name=''):
    """
    Run autoworkup on a single session

    This is the main function to call when processing a data set with T1 & T2
    data.  ExperimentBaseDirectoryPrefix is the base of the directory to place results, T1Images & T2Images
    are the lists of images to be used in the auto-workup. atlas_fname_wpath is
    the path and filename of the atlas to use.
    """
    assert 'auxlmk' in config['components'] or 'tissue_classify' in config['components'], \
      "DataSink requires 'AUXLMK' or 'TISSUE_CLASSIFY'"

    from nipype.interfaces.base import CommandLine, CommandLineInputSpec, TraitedSpec, Directory
    from nipype.interfaces.base import traits, isdefined, BaseInterface
    from nipype.interfaces.utility import Split, Rename, IdentityInterface, Function
    import nipype.pipeline.engine as pe
    import nipype.interfaces.io as nio
    from phase1_singleSession import get_list_element, getAllT1sLength  # Can we replace with len()?
    from utilities.misc import GenerateWFName
    from PipeLineFunctionHelpers import convertToList, UnwrapPosteriorImagesFromDictionaryFunction

    T1T2WorkupSingle = pe.Workflow(name=pipeline_name)

    inputsSpec = pe.Node(interface=IdentityInterface(fields=['atlasLandmarkFilename', 'atlasWeightFilename',
                                                             'LLSModel', 'inputTemplateModel', 'template_t1',
                                                             'atlasDefinition', 'T1s', 'T2s', 'PDs', 'FLs', 'OTHERs']),
                         run_without_submitting=True, name='inputspec')

    outputsSpec = pe.Node(interface=IdentityInterface(fields=['t1_average', 't2_average', 'pd_average', 'fl_average',
                                                              'posteriorImages', 'outputLabels', 'outputHeadLabels',
                                                              'TissueClassifyatlasToSubjectTransform',
                                                              'TissueClassifyatlasToSubjectInverseTransform',
                                                              'BCD_ACPC_T1_CROPPED',
                                                              'outputLandmarksInACPCAlignedSpace',
                                                              'outputLandmarksInInputSpace',
                                                              'outputTransform', 'LMIatlasToSubjectTransform',
                                                              'writeBranded2DImage'
                                                              ]),
                          run_without_submitting=True, name='outputspec')

    from WorkupT1T2LandmarkInitialization import CreateLandmarkInitializeWorkflow
    DoReverseMapping = False   # Set to true for debugging outputs
    if 'auxlmk' in config['components']:
        DoReverseMapping = True
    myLocalLMIWF = CreateLandmarkInitializeWorkflow("LandmarkInitialize", interpMode, DoReverseMapping)

    T1T2WorkupSingle.connect([(inputsSpec, myLocalLMIWF,
                               [(('T1s', get_list_element, 0), 'inputspec.inputVolume'),
                                ('atlasLandmarkFilename', 'inputspec.atlasLandmarkFilename'),
                                ('atlasWeightFilename', 'inputspec.atlasWeightFilename'),
                                ('LLSModel', 'inputspec.LLSModel'),
                                ('inputTemplateModel', 'inputspec.inputTemplateModel'),
                                ('template_t1', 'inputspec.atlasVolume')]
                            )])

    if 'auxlmk' in config['components']:
        T1T2WorkupSingle.connect([(myLocalLMIWF, outputsSpec, [('outputspec.outputResampledCroppedVolume',
                                                                'BCD_ACPC_T1_CROPPED'),
                                                               ('outputspec.outputLandmarksInACPCAlignedSpace',
                                                                'outputLandmarksInACPCAlignedSpace'),
                                                               ('outputspec.outputLandmarksInInputSpace',
                                                                'outputLandmarksInInputSpace'),
                                                               ('outputspec.outputTransform', 'outputTransform'),
                                                               ('outputspec.atlasToSubjectTransform',
                                                                'LMIatlasToSubjectTransform'),
                                                               ('outputspec.writeBranded2DImage', 'writeBranded2DImage')]
                                )])

    if 'tissue_classify' in config['components']:
        from WorkupT1T2TissueClassify import CreateTissueClassifyWorkflow
        myLocalTCWF = CreateTissueClassifyWorkflow("TissueClassify", config['queue'], config['long_q'], interpMode)

        T1T2WorkupSingle.connect([(inputsSpec, myLocalTCWF, [('atlasDefinition', 'inputspec.atlasDefinition'),
                                                             ('T1s', 'inputspec.T1List'),
                                                             (('T1s', getAllT1sLength), 'inputspec.T1_count'),  # (('T1s', len), 'inputspec.T1_count'),
                                                             ('T2s', 'inputspec.T2List'),
                                                             ('PDs', 'inputspec.PDList'),
                                                             ('FLs', 'inputspec.FLList'),
                                                             ('OTHERs', 'inputspec.OtherList')])
                                 ])

        T1T2WorkupSingle.connect([(myLocalLMIWF, myLocalTCWF,
                                   [('outputspec.outputResampledCroppedVolume', 'inputspec.PrimaryT1'),
                                    ('outputspec.atlasToSubjectTransform', 'inputspec.atlasToSubjectInitialTransform')]
                                  )])

        T1T2WorkupSingle.connect([(myLocalTCWF, outputsSpec, [('outputspec.t1_average', 't1_average'),
                                                              ('outputspec.t2_average', 't2_average'),
                                                              ('outputspec.pd_average', 'pd_average'),
                                                              ('outputspec.fl_average', 'fl_average'),
                                                              ('outputspec.posteriorImages', 'posteriorImages'),
                                                              ('outputspec.outputLabels', 'outputLabels'),
                                                              ('outputspec.outputHeadLabels', 'outputHeadLabels'),
                                                              ('outputspec.atlasToSubjectTransform',
                                                               'TissueClassifyatlasToSubjectTransform'),
                                                              ('outputspec.atlasToSubjectInverseTransform',
                                                               'TissueClassifyatlasToSubjectInverseTransform')]
                                  )])

    dsName = "{0}_ds_{1}".format(phase, sessionid)
    DataSink = pe.Node(name=dsName, interface=nio.DataSink())
    DataSink.overwrite = config['ds_overwrite']
    DataSink.inputs.container = '{0}/{1}/{2}'.format(projectid, subjectid, sessionid)
    DataSink.inputs.base_directory = config['resultdir']

    T1T2WorkupSingle.connect([(outputsSpec, DataSink,
                               [(('t1_average', convertToList), 'Phase_1.@t1_average'),
                                (('t2_average', convertToList), 'Phase_1.@t2_average'),
                                (('pd_average', convertToList), 'Phase_1.@pd_average'),
                                (('fl_average', convertToList), 'Phase_1.@fl_average'),
                                (('outputLabels', convertToList), 'Phase_1.@labels'),
                                (('posteriorImages', UnwrapPosteriorImagesFromDictionaryFunction),'Phase_1.TissueClassify')]),
                             ])
    return T1T2WorkupSingle
