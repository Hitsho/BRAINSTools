import os
#######################  HACK:  Needed to make some global variables for quick
#######################         processing needs
# Generate by running a file system list "ls -1 $AtlasDir *.nii.gz *.xml *.fcsv *.wgts"
# atlas_file_names=atlas_file_list.split(' ')
## HACK
atlas_file_names = ["ExtendedAtlasDefinition.xml", "ExtendedAtlasDefinition.xml.in",
                    "avg_t1.nii.gz", "avg_t2.nii.gz", "tempNOTVBBOX.nii.gz",
                    "template_ABC_labels.nii.gz", "template_WMPM2_labels.nii.gz",
                    "template_WMPM2_labels.txt", "template_brain.nii.gz",
                    "template_cerebellum.nii.gz", "template_class.nii.gz",
                    "template_headregion.nii.gz", "template_leftHemisphere.nii.gz",
                    "template_nac_labels.nii.gz", "template_nac_labels.txt",
                    "hncma-atlas.nii.gz", "hncma-atlas-lut-mod2.ctbl",
                    "template_rightHemisphere.nii.gz", "template_t1.nii.gz",
                    "template_t1_clipped.nii.gz", "template_t2.nii.gz",
                    "template_t2_clipped.nii.gz", "template_ventricles.nii.gz",

                    "probabilityMaps/l_accumben_ProbabilityMap.nii.gz",
                    "probabilityMaps/r_accumben_ProbabilityMap.nii.gz",
                    "probabilityMaps/l_caudate_ProbabilityMap.nii.gz",
                    "probabilityMaps/r_caudate_ProbabilityMap.nii.gz",
                    "probabilityMaps/l_globus_ProbabilityMap.nii.gz",
                    "probabilityMaps/r_globus_ProbabilityMap.nii.gz",
                    "probabilityMaps/l_hippocampus_ProbabilityMap.nii.gz",
                    "probabilityMaps/r_hippocampus_ProbabilityMap.nii.gz",
                    "probabilityMaps/l_putamen_ProbabilityMap.nii.gz",
                    "probabilityMaps/r_putamen_ProbabilityMap.nii.gz",
                    "probabilityMaps/l_thalamus_ProbabilityMap.nii.gz",
                    "probabilityMaps/r_thalamus_ProbabilityMap.nii.gz",

                    "spatialImages/phi.nii.gz",
                    "spatialImages/rho.nii.gz",
                    "spatialImages/theta.nii.gz",

                    "modelFiles/trainModelFile.txtD0060NT0060.gz",
                    "20111119_BCD/LLSModel_50Lmks.hdf5",
                    "20111119_BCD/T1_50Lmks.mdl",
                    "20111119_BCD/template_landmarks_50Lmks.fcsv",
                    "20111119_BCD/template_weights_50Lmks.wts"
                    ]
## Remove filename extensions for images, but replace . with _ for other file types
atlas_file_keys = [os.path.basename(fn).replace('.nii.gz', '').replace('.', '_') for fn in atlas_file_names]
atlas_outputs_filename_match = dict(zip(atlas_file_keys, atlas_file_names))
