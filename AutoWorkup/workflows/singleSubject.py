# def getAllFiles(database):
#     T1s = database.getFilenamesByScantype(session, ['T1-15', 'T1-30'])
#     ...
#     return (T1s, ...)

def RunSubjectWorkflow(args):
    """
                           .-----------.
                       --- | Session 1 | ---> /project/subjectA/session1/Phase_1/
                     /     *-----------*
    .-----------.   /
    | Subject A | <
    *-----------*   \
                     \     .-----------.
                       --- | Session 2 | ---> /project/subjectA/session2/Phase_1/
                           *-----------*
    * Replaces WorkflowT1T2.py for 'Phase 1/Baseline'
    """
    database, start_time, subject, master_config = args
    # HACK:
    #  To avoid a "sqlite3.ProgrammingError: Base Cursor.__init__ not called" error
    #  using multiprocessing.map_async(), re-instantiate database
    database.__init__(defaultDBName=database.dbName, subject_list=database.subjectList)
    # END HACK
    assert 'phase1' in master_config['components'], "Phase 1 is not in WORKFLOW_COMPONENTS!"

    import time
    import traceback
    import sys

    # Set universal pipeline options
    from nipype import config
    config.update_config(master_config)
    assert config.get('execution', 'plugin') == master_config['execution']['plugin']

    import nipype.pipeline.engine as pe
    import nipype.interfaces.base as nbase
    import nipype.interfaces.io as nio
    from nipype.interfaces.utility import IdentityInterface, Function
    import traits

    from baw_exp import OpenSubjectDatabase
    from SessionDB import SessionDB
    from PipeLineFunctionHelpers import convertToList
    from atlasNode import MakeAtlasNode
    from phase1_singleSession import sessionWorkflow as phase1_wkfl

    while time.time() < start_time:
        time.sleep(start_time - time.time() + 1)
        print "Delaying start for {subject}".format(subject=subject)
    print("===================== SUBJECT: {0} ===========================".format(subject))

    subjectWorkflow = pe.Workflow(name="BAW_StandardWorkup_subject_{0}".format(subject))
    subjectWorkflow.base_dir = master_config['logging']['log_directory']

    atlasNode = MakeAtlasNode(master_config['atlascache'], 'BAtlas')

    sessionWorkflow = dict()
    inputsSpec = dict()
    sessions = database.getSessionsFromSubject(subject)
    # print "These are the sessions: ", sessions
    from utilities.misc import GenerateWFName

    for session in sessions:  # TODO: Replace with iterable inputSpec node and add Function node for getAllFiles()
        project = database.getProjFromSession(session)
        pname = GenerateWFName(project, subject, session, 'phase1')
        print "Building session pipeline for {0}".format(session)
        inputsSpec[session] = pe.Node(name='inputspec_{0}'.format(session),
                                      interface=IdentityInterface(fields=['T1s', 'T2s', 'PDs', 'FLs', 'OTs']))
        inputsSpec[session].inputs.T1s = database.getFilenamesByScantype(session, ['T1-15', 'T1-30'])
        inputsSpec[session].inputs.T2s = database.getFilenamesByScantype(session, ['T2-15', 'T2-30'])
        inputsSpec[session].inputs.PDs = database.getFilenamesByScantype(session, ['PD-15', 'PD-30'])
        inputsSpec[session].inputs.FLs = database.getFilenamesByScantype(session, ['FL-15', 'FL-30'])
        inputsSpec[session].inputs.OTs = database.getFilenamesByScantype(session, ['OTHER-15', 'OTHER-30'])

        sessionWorkflow[session] = phase1_wkfl(project, subject, session, 'phase1', master_config, interpMode='Linear',
                                               pipeline_name=pname)

        subjectWorkflow.connect([(inputsSpec[session], sessionWorkflow[session], [('T1s', 'inputspec.T1s'),
                                                                                  ('T2s', 'inputspec.T2s'),
                                                                                  ('PDs', 'inputspec.PDs'),
                                                                                  ('FLs', 'inputspec.FLs'),
                                                                                  ('OTs', 'inputspec.OTHERs'),
                                                                                  ]),
                                 (atlasNode, sessionWorkflow[session], [('template_landmarks_50Lmks_fcsv',
                                                                         'inputspec.atlasLandmarkFilename'),
                                                                        ('template_weights_50Lmks_wts',
                                                                         'inputspec.atlasWeightFilename'),
                                                                        ('LLSModel_50Lmks_hdf5', 'inputspec.LLSModel'),
                                                                        ('T1_50Lmks_mdl', 'inputspec.inputTemplateModel'),
                                                                        ('template_t1', 'inputspec.template_t1'),
                                                                        ('ExtendedAtlasDefinition_xml',
                                                                         'inputspec.atlasDefinition'),
                                                                        ]),
                                 ])

    if master_config['execution']['plugin'] in ['Linear', 'MultiProc']:
        try:
            print "Writing out graph!"
            graphtype = 'hierarchical'
            subjectWorkflow.write_graph(dotfilename='subject', graph2use=graphtype)
        except:
            raise
    try:
        print "Running workflow..."
        if not master_config['execution']['plugin'] in ['Linear', 'MultiProc']:
            subjectWorkflow.run(plugin_args=master_config['plugin_args'])
        else:
            print "HERE I AM!"
            subjectWorkflow.run()
    except:
        print "=+-+" * 25
        print ("Error: Exception while running subject {0}".format(subject))
        traceback.print_exc(file=sys.stdout)
        return False
    return True
