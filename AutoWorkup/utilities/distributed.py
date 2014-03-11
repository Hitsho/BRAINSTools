def load_cluster(modules=[]):
    if len(modules) > 0:
        module_list = []
        for module in modules:
            module_list.append("module load {name}".format(name=module))
        assert len(modules) == len(module_list)
        return '\n'.join(module_list)
    return ''


def source_virtualenv(virtualenv=''):
    if virtualenv is None:
        return ''
    assert virtualenv != ''
    return "source {0}".format(virtualenv)


def prepend_env(environment={}):
    import os
    export_list = []
    for key, value in environment.items():
        export_list.append("export {key}={value}{sep}${key}".format(key=key, value=value, sep=os.pathsep))  # Append to variable
    return '\n'.join(export_list)


def create_global_sge_script(cluster, environment):
    """ This is a wrapper script for running commands on an SGE cluster
    so that all the python modules and commands are pathed properly """
    import os
    from string import Template
    import sys

    sub_dict = dict(LOAD_MODULES=load_cluster(cluster['modules']),
                    VIRTUALENV=source_virtualenv(environment['virtualenv']),
                    EXPORT_ENV=prepend_env(environment['env']))
    with open(os.path.join(os.path.dirname(__file__), 'node.sh.template')) as fid:
        tpl = fid.read()
    retval = Template(tpl).substitute(sub_dict)
    # print "="*100
    # print retval
    # print "="* 100
    return retval
