#! /usr/bin/env python
"""
phase1.py
=========
This program is used to generate the subject- and session-specific workflows for BRAINSTool processing

Usage:
  phase1.py [--rewrite-datasinks] [--wfrun PLUGIN] --subject ID... --pe ENV --ExperimentConfig FILE
  phase1.py -v | --version
  phase1.py -h | --help

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
  $ phase1.py --subject 1058 --pe OSX --ExperimentConfig my_baw.config
  $ phase1.py --wfrun helium_all.q --subject 1058 --pe OSX --ExperimentConfig my_baw.config
  $ phase1.py --rewrite-datasinks --subject 1058 --pe OSX --ExperimentConfig my_baw.config

"""

##########################################################################################################
# def phase1(args):                                                                                      #
#     database, subjectid, sessions, processing_phase, config, interpMode, pipeline_name = *args         #
#     import nipype.pipeline.engine as pe                                                                #
#     from nipype.interfaces.utility import Function                                                     #
#                                                                                                        #
#     from phase1_singleSession import sessionWorkFlow                                                   #
#                                                                                                        #
#     phase1 = pe.Workflow(name='Subject_{0}_Phase1'.format(subject))                                    #
#                                                                                                        #
#     sessionsWkfl = pe.MapNode(name="PHASE_1_sessions",                                                 #
#                               interface=Function(function=sessionWorkFlow,                             #
#                                                  input_names=['projectid', 'subjectid',                #
#                                                               'sessionid', 'database', 'phase',        #
#                                                               'config', 'interpMode', 'pipeline_name'] #
#                                                  output_names=['T1T2WorkupSingle']),                   #
#                               iterfield=['sessionid'])                                                 #
#     sessionsWkfl.inputs.sessionid = sessions                                                           #
#     return sessionsWkfl                                                                                #
##########################################################################################################


if __name__ == '__main__':
    import subprocess
    import sys
    import os, os.path

    from docopt import docopt

    assert os.getcwd() == os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    argv = docopt(__doc__, version='1.1')
    cmd = ['python', 'AutoWorkup.py']
    for key, value in argv.items():
        if value is None:
            continue
        elif isinstance(value, list):
            cmd.append(key)
            for item in value:
                cmd.append(str(item))
        elif isinstance(value, bool):
            if value:
                cmd.append(key)
        else:
            cmd.append(key)
            cmd.append(value)
    print ' '.join(cmd)

    sys.exit(subprocess.check_call(cmd))
