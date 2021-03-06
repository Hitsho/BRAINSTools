include_directories(
  ${BRAINSTools_SOURCE_DIR}/BRAINSABC/brainseg
  ${BRAINSTools_SOURCE_DIR}/BRAINSABC/common
  ${BRAINSTools_BINARY_DIR}/BRAINSABC/brainseg
  )



MakeTestDriverFromSEMTool(BRAINSABC BRAINSABCTest.cxx)

ExternalData_add_test( ${PROJECT_NAME}FetchData NAME BRAINSABCSmallTest
  COMMAND ${LAUNCH_EXE} $<TARGET_FILE:BRAINSABCTestDriver>
  --compare DATA{${TestData_DIR}/BRAINSABCSmallLabels.nii.gz}
  ${CMAKE_CURRENT_BINARY_DIR}/BRAINSABCSmallLabels.test.nii.gz
  --compareIntensityTolerance 1
  --compareRadiusTolerance 1
  --compareNumberOfPixelsTolerance 10000
  BRAINSABCTest
   --atlasDefinition DATA{${TestData_DIR}/BRAINSABCSmallExtendedAtlasDefinition.xml}
   --atlasToSubjectInitialTransform DATA{${TestData_DIR}/BRAINSABCSmall_atlas_to_subject_transform.h5}
   --atlasToSubjectTransform BRAINSABCSmall_atlas_to_subject_transform.h5
   --atlasToSubjectTransformType Affine
   --debuglevel 0
   --filterIteration 0
   --filterMethod GradientAnisotropicDiffusion
   --gridSize 10,10,10
   --inputVolumeTypes T1,T1,T2
   --inputVolumes DATA{${TestData_DIR}/BRAINSABCSmall_T1.nii.gz}
   --inputVolumes DATA{${TestData_DIR}/BRAINSABCSmall_T1_offset.nii.gz}
   --inputVolumes DATA{${TestData_DIR}/BRAINSABCSmall_T2.nii.gz}
   --interpolationMode Linear
   --maxBiasDegree 4
   --maxIterations 3
   --outputDir ./
   --outputDirtyLabels ${CMAKE_CURRENT_BINARY_DIR}/BRAINSABCSmallvolume_label_seg.nii.gz
   --outputFormat NIFTI
   --outputLabels ${CMAKE_CURRENT_BINARY_DIR}/BRAINSABCSmallLabels.test.nii.gz
   --outputVolumes ${CMAKE_CURRENT_BINARY_DIR}/BRAINSABCSmallT1_1.nii.gz
   --outputVolumes ${CMAKE_CURRENT_BINARY_DIR}/BRAINSABCSmallT1_2.nii.gz
   --outputVolumes ${CMAKE_CURRENT_BINARY_DIR}/BRAINSABCSmallT2_1.nii.gz
   --posteriorTemplate ${CMAKE_CURRENT_BINARY_DIR}/BRAINSABCSmallPOST_%s.nii.gz
)

if( ${BRAINSTools_MAX_TEST_LEVEL} GREATER 5) #These test takes way to long to run all the time
ExternalData_add_test( ${PROJECT_NAME}FetchData NAME BRAINSABCLongTest
  COMMAND ${LAUNCH_EXE} $<TARGET_FILE:BRAINSABCTestDriver>
  --compare DATA{${TestData_DIR}/labels.nii.gz}
  ${CMAKE_CURRENT_BINARY_DIR}/labels.nii.gz
  --compareIntensityTolerance 1
  --compareRadiusTolerance 1
  --compareNumberOfPixelsTolerance 10000
  BRAINSABCTest
  --inputVolumes DATA{${TestData_DIR}/small_ISO_T1_REP0.nii.gz}
  --inputVolumes DATA{${TestData_DIR}/small_ISO_T2_REP0.nii.gz}
  --outputVolumes ${CMAKE_CURRENT_BINARY_DIR}/T1_cleaned.nii.gz,${CMAKE_CURRENT_BINARY_DIR}/T2_cleaned.nii.gz
  --outputLabels ${CMAKE_CURRENT_BINARY_DIR}/labels.nii.gz
  --outputDirtyLabels ${CMAKE_CURRENT_BINARY_DIR}/dirty_labels.nii.gz
  --posteriorTemplate ${CMAKE_CURRENT_BINARY_DIR}/POST_%s.nii.gz
  --inputVolumeTypes T1,T2
  --filterIteration 3
  --maxIterations 2
  --maxBiasDegree 2
  --debuglevel 0
  --outputFormat NIFTI
  --outputDir ${CMAKE_CURRENT_BINARY_DIR}
  --gridSize  5,3,4
  --atlasDefinition ${ReferenceAtlas_DIR}/${ATLAS_NAME}/AtlasPVDefinition.xml
  )
ExternalData_add_test( ${PROJECT_NAME}FetchData NAME BRAINSABCLongTest2
  COMMAND ${LAUNCH_EXE} $<TARGET_FILE:BRAINSABCTestDriver>
  --compare DATA{${TestData_DIR}/labels.nii.gz}
  ${CMAKE_CURRENT_BINARY_DIR}/labels.nii.gz
  --compareIntensityTolerance 1
  --compareRadiusTolerance 1
  --compareNumberOfPixelsTolerance 10000
  BRAINSABCTest
  --inputVolumes DATA{${TestData_DIR}/small_ISO_T1_REP0.nii.gz}
  --inputVolumes DATA{${TestData_DIR}/small_ISO_T1_REP0.nii.gz}
  --inputVolumes DATA{${TestData_DIR}/small_ISO_T2_REP0.nii.gz}
  --inputVolumes DATA{${TestData_DIR}/small_ISO_T2_REP0.nii.gz}
  --outputVolumes ${CMAKE_CURRENT_BINARY_DIR}/T1_cleaned.nii.gz,${CMAKE_CURRENT_BINARY_DIR}/T1_cleaned2.nii.gz,${CMAKE_CURRENT_BINARY_DIR}/T2_cleaned.nii.gz,${CMAKE_CURRENT_BINARY_DIR}/T2_cleaned2.nii.gz
  --outputLabels ${CMAKE_CURRENT_BINARY_DIR}/labels.nii.gz
  --outputDirtyLabels ${CMAKE_CURRENT_BINARY_DIR}/dirty_labels.nii.gz
  --posteriorTemplate ${CMAKE_CURRENT_BINARY_DIR}/POST_%s.nii.gz
  --inputVolumeTypes T1,T1,T2,T2
  --filterIteration 3
  --maxIterations 2
  --maxBiasDegree 2
  --debuglevel 0
  --outputFormat NIFTI
  --outputDir ${CMAKE_CURRENT_BINARY_DIR}
  --gridSize  5,3,4
  --atlasDefinition ${ReferenceAtlas_DIR}/${ATLAS_NAME}/AtlasPVDefinition.xml
  )
set_tests_properties(BRAINSABCLongTest PROPERTIES TIMEOUT 6500)
endif()

if( ${BRAINSTools_MAX_TEST_LEVEL} GREATER 8) # This should be restored after fixing.
  add_executable(BlendImageFilterTest BlendImageFilterTest.cxx)
  target_link_libraries(BlendImageFilterTest ${ITK_LIBRARIES})
  ExternalData_add_test( ${PROJECT_NAME}FetchData NAME BlendImageFilterTest COMMAND ${LAUNCH_EXE}  $<TARGET_FILE:BlendImageFilterTest> )
endif()

## - ExternalData_Add_Target( ${PROJECT_NAME}FetchData )  # Name of data management target
