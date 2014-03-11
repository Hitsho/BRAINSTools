def MakeAtlasNode(atlasDirectory, name):
    import nipype.interfaces.io as nio   # Data i/o
    import nipype.pipeline.engine as pe  # pypeline engine

    from utilities import atlas_file_names, atlas_file_keys, atlas_outputs_filename_match

    node = pe.Node(interface=nio.DataGrabber(outfields=atlas_file_keys),
                     run_without_submitting=True,
                     name=name)
    node.inputs.base_directory = atlasDirectory
    node.inputs.sort_filelist = False
    node.inputs.template = '*'
    ## Prefix every filename with atlasDirectory
    atlas_search_paths = ['{0}'.format(fn) for fn in atlas_file_names]
    node.inputs.field_template = dict(zip(atlas_file_keys, atlas_search_paths))
    ## Give 'atlasDirectory' as the substitution argument
    atlas_template_args_match = [ [[]] for i in atlas_file_keys]  # build a list of proper length with repeated entries
    node.inputs.template_args = dict(zip(atlas_file_keys, atlas_template_args_match))
    node.run()
    # print "+" * 100
    # print node.inputs
    # print "-" * 100
    return node
