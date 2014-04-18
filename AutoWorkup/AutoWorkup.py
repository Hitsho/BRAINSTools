#! /usr/bin/env python
"""
AutoWorkup.py
====================
This program is used to generate the subject- and session-specific workflows for BRAINSTool processing

Usage:
  AutoWorkup.py [--rewrite-datasinks] [--wfrun PLUGIN] --subject ID... --pe ENV --ExperimentConfig FILE
  AutoWorkup.py -v | --version
  AutoWorkup.py -h | --help

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
  $ AutoWorkup.py --subject 1058 --pe OSX --ExperimentConfig my_baw.config
  $ AutoWorkup.py --wfrun helium_all.q --subject 1058 --pe OSX --ExperimentConfig my_baw.config
  $ AutoWorkup.py --rewrite-datasinks --subject 1058 --pe OSX --ExperimentConfig my_baw.config

"""
from baw_exp import OpenSubjectDatabase

def load_modules(modules):
    """ The command 'module' is actually a script call in bash:

    module=() {eval `/opt/modules/Modules/$MODULE_VERSION/bin/modulecmd bash $* }`

    So running os.execvp() on it doesn't work without the correct file path to the module executable """
    for module in modules:
        os.system(" ".join(['module load', module]))  # os.execv(module_exe, 'bash', 'load', module])

def setupEnvironment(argv):
    environment, experiment, pipeline, cluster = parseFile(argv["--ExperimentConfig"], argv["--pe"], argv['--wfrun'])
    pipeline['ds_overwrite'] = resolveDataSinkOption(argv, pipeline)
    if cluster is None:
        assert argv["--wfrun"] in misc.WFRUN, \
          "wfrun options for clusters can only be given when the configuration file's CLUSTER option == True"
        os.environ['NSLOTS'] = str(misc.get_cpus(argv["--wfrun"]))
    else:
        load_modules(cluster['modules'])  # Load modules if not already done  ## MODS PATH
        # print os.environ['LOADEDMODULES']
    if environment['virtualenv']:  ## MODS PATH
        activate_this = validatePath(os.path.join(environment['virtualenv'], 'bin', 'activate_this.py'))
        execfile(activate_this, dict(__file__=activate_this))
    utilities_path = os.path.dirname(os.path.abspath(__file__))
    configure_env = validatePath(os.path.join(utilities_path, 'utilities', 'configure_env.py'))
    execfile(configure_env, dict(__file__=configure_env,
                                 append_os_path=environment['env']['PATH'],
                                 append_sys_path=environment['env']['PYTHONPATH'])
        )  ## MODS PATH
    from nipype import config
    config.enable_debug_mode()
    from utilities.package_check import verify_packages
    verify_packages()
    if 'FREESURFER' in experiment['components']:  ## FREESURFER MODS
        configure_FS = validatePath(os.path.join(utilities_path, 'utilities', 'configure_FS.py'))
        execfile(configure_FS, dict(FS_VARS=misc.FS_VARS, env=environment['env']))
        print "FREESURFER needs to check for sane environment here!"  # TODO: raise warning, write method, what???

    for key, value in environment['env'].items():
        if key in ['PATH', 'PYTHONPATH'] + misc.FS_VARS:
            pass
        else:
            os.environ[key] = value  # Do not use os.putenv (see Python documentation)
    return environment, experiment, pipeline, cluster


def get_subjects(argv, cache, prefix, dbfile, shuffle=True):
    import random

    _temp = OpenSubjectDatabase(cache, ['all'], prefix, dbfile)
    subjects = argv["--subject"]  #.split(',')
    if "all" in subjects:
        subjects = _temp.getAllSubjects()
    if shuffle:
        random.shuffle(subjects)  # randomly shuffle to get max
    return subjects


if __name__ == "__main__":
    import os.path
    import sys
    import time
    from docopt import docopt
    from utilities.configFileParser import parseFile, resolveDataSinkOption, nipype_options
    from utilities.pathHandling import validatePath
    from utilities import misc
    from utilities import distributed as dstb
    from workflows import singleSubject as ss

    argv = docopt(__doc__, version='1.1')  # Get argv as dictionary
    # print argv
    # print '=' * 100
    print "Configuring environment..."
    environment, experiment, pipeline, cluster = setupEnvironment(argv)
    # for key, value in os.environ.items():
    #     print key, " = ", value
    # print sys.path
    print "Getting subjects from database..."
    subjects = get_subjects(argv, experiment['cachedir'], environment['prefix'], experiment['dbfile']) # Build database before parallel section
    if environment['cluster']:
        print "Creating node template string..."
        node_template = dstb.create_global_sge_script(cluster, environment)  # vs. os.environ)
    else:
        node_template = None
    print "Determining appropriate Nipype options..."
    pipeline = nipype_options(argv, pipeline, cluster, node_template, experiment)  # Generate Nipype options

    master_config = {}
    for configDict in [environment, experiment, pipeline, cluster]:
        master_config = misc.add_dict(master_config, configDict)

    sp_args_list = []
    current_time = time.time()
    index = 0
    delay = 2.5
    for subject in subjects:
        index += 1
        print ("START DELAY: {0}".format(delay))
        database = OpenSubjectDatabase(master_config['cachedir'], [subject], master_config['prefix'], master_config['dbfile'])  # Get DB object before parallel section
        # print database.getAllSessions()
        start_time = current_time + (index * delay)
        sp_args = (database, start_time, subject, master_config)
        sp_args_list.append(sp_args)

    print "Running workflow(s) now..."

    if argv["--wfrun"].startswith('local'):
        for args in sp_args_list:
            ss.RunSubjectWorkflow(args)
    else:
        from multiprocessing import Pool
        myPool = Pool(processes=64, maxtasksperchild=1)
        try:
            all_results = myPool.map_async(ss.RunSubjectWorkflow, sp_args_list).get(1e100)
        except ValueError, err:
            err.msg += "\nArgs to map_async: {0}".format(sp_args_list)
            raise err
        for index in range(len(sp_args_list)):
            if all_results[index] == False:
                print "FAILED for {0}".format(sp_args_list[index][-1])

    print("THIS RUN OF BAW FOR SUBJS {0} HAS COMPLETED".format(subjects))
    sys.exit(0)
