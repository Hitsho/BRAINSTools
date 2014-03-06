#include "BRAINSStripRotationCLP.h"
#include "itkImageIOFactory.h"
#include "itkIO.h"
#include "itkTransformFileWriter.h"
#include "itkRigid3DTransform.h"
#include "itkRigid2DTransform.h"

template<typename TPrecision>
itk::TransformBaseTemplate<TPrecision> *
NewTransform(const typename itk::Image<char,3>::DirectionType &dir)
{
  typedef itk::Rigid3DTransform<TPrecision> TransformType;
  typename TransformType::Pointer rval = TransformType::New();
  rval->SetMatrix(dir);
  std::cerr << rval
            << rval->GetMatrix()
            << std::endl;
  rval.GetPointer()->Register();
  return rval.GetPointer();
}

template<typename TPrecision>
itk::TransformBaseTemplate<TPrecision> *
NewTransform(const typename itk::Image<char,2>::DirectionType &dir)
{
  typedef itk::Rigid2DTransform<TPrecision> TransformType;
  typename TransformType::Pointer rval = TransformType::New();
  rval->SetMatrix(dir);
  std::cerr << rval
            << rval->GetMatrix()
            << std::endl;
  return rval;
}

template<typename TImage>
int
ReadAndSplitImage(const std::string &inputVolume,
                  const std::string &outputVolume,
                  const std::string &transform)
{
  typedef TImage ImageType;
  typename ImageType::Pointer inputImage;
  try
    {
    inputImage = itkUtil::ReadImage<ImageType>(inputVolume);
    }
  catch( itk::ExceptionObject & err )
    {
    std::cerr << "Error reading " << inputVolume
              << err.what() << std::endl;
    return 1;
    }
  catch(...)
    {
    std::cerr << "Error reading " << inputVolume
              << std::endl;
    return 1;
    }
  const typename ImageType::DirectionType &direction = inputImage->GetDirection();
  typename ImageType::DirectionType id;
  id.SetIdentity();
  inputImage->SetDirection(id);
  try
    {
    itkUtil::WriteImage<ImageType>(inputImage,outputVolume);
    }
  catch( itk::ExceptionObject & err )
    {
    std::cerr << "Error writing " << outputVolume
              << err.what() << std::endl;
    return 1;
    }
  catch(...)
    {
    std::cerr << "Error writing " << outputVolume
              << std::endl;
    return 1;
    }
  typedef typename ImageType::DirectionType::ValueType XFRMPrecisionType;

  std::cerr << "sizeof(XFRMPrecisionType = " << sizeof(XFRMPrecisionType) << std::endl;

  typedef itk::TransformFileWriterTemplate<XFRMPrecisionType> TransformFileWriterType;

  typedef typename TransformFileWriterType::TransformType TransformType;

  typename TransformFileWriterType::Pointer xfrmWriter = TransformFileWriterType::New();

  // create a rigid transform from the direction matrix.
  typename TransformType::Pointer xfrm = NewTransform<XFRMPrecisionType>(direction);

  xfrmWriter->SetInput(xfrm.GetPointer());

  xfrmWriter->SetFileName(transform);
  try
    {
    xfrmWriter->Update();
    }
  catch( itk::ExceptionObject & err )
    {
    std::cerr << "Error writing " << transform
              << err.what() << std::endl;
    return 1;
    }
  catch(...)
    {
    std::cerr << "Error writing " << transform
              << std::endl;
    return 1;
    }

  return 0;
}

int main(int argc, char *argv[])
{
  PARSE_ARGS;
  if(inputVolume == "")
    {
    std::cerr << "Missing input volume name" << std::endl;
    return 1;
    }
  if(outputVolume == "")
    {
    std::cerr << "Missing output volume name" << std::endl;
    return 1;
    }
  if(transform == "")
    {
    std::cerr << "Missing transform file name" << std::endl;
    return 1;
    }
  //
  // have to find out what type of file this is.
  itk::ImageIOBase::Pointer imageIO =
    itk::ImageIOFactory::CreateImageIO(inputVolume.c_str(),itk::ImageIOFactory::ReadMode);
  if(imageIO.IsNotNull())
    {
    try
      {
      imageIO->SetFileName(inputVolume);
      imageIO->ReadImageInformation();
      }
    catch(itk::ExceptionObject &excp)
      {
      std::cerr << "itkLoadWithMetaData: can't read "
                << inputVolume << " "
                << excp.what() << std::endl;
      return 1;
      }
    }
  else  // can't find proper reader for file
    {
    std::cerr << "Can't file ITK reader for "
              << inputVolume << std::endl;
    return 1;
    }
  //
  // For now support scalar images of 2 or 3 dimensions.  Adding more
  // isn't a problem, but it complicates how we build the matlab structure.
  itk::ImageIOBase::IOPixelType pixtype = imageIO->GetPixelType();
  itk::ImageIOBase::IOComponentType componentType = imageIO->GetComponentType();
  if(pixtype != itk::ImageIOBase::SCALAR)
    {
    std::cerr << "Unsupported pixel type " << itk::ImageIOBase::GetPixelTypeAsString(pixtype)
              << " in volume " << inputVolume << std::endl;
    return 1;
    }
  unsigned imageDimension = imageIO->GetNumberOfDimensions();
  switch(imageDimension)
    {
    case 2:
      switch(componentType)
        {
        case itk::ImageIOBase::UCHAR:
          return ReadAndSplitImage<itk::Image<unsigned char,2> >(inputVolume,outputVolume,transform);
          break;
        case itk::ImageIOBase::CHAR:
          return ReadAndSplitImage<itk::Image<char,2> >(inputVolume,outputVolume,transform);
          break;
        case itk::ImageIOBase::USHORT:
          return ReadAndSplitImage<itk::Image<unsigned short,2> >(inputVolume,outputVolume,transform);
          break;
        case itk::ImageIOBase::SHORT:
          return ReadAndSplitImage<itk::Image<short,2> >(inputVolume,outputVolume,transform);
          break;
        case itk::ImageIOBase::UINT:
          return ReadAndSplitImage<itk::Image<unsigned int,2> >(inputVolume,outputVolume,transform);
          break;
        case itk::ImageIOBase::INT:
          return ReadAndSplitImage<itk::Image<int,2> >(inputVolume,outputVolume,transform);
          break;
        case itk::ImageIOBase::ULONG:
          return ReadAndSplitImage<itk::Image<unsigned long,2> >(inputVolume,outputVolume,transform);
          break;
        case itk::ImageIOBase::LONG:
          return ReadAndSplitImage<itk::Image<long,2> >(inputVolume,outputVolume,transform);
          break;
        case itk::ImageIOBase::FLOAT:
          return ReadAndSplitImage<itk::Image<float,2> >(inputVolume,outputVolume,transform);
          break;
        case itk::ImageIOBase::DOUBLE:
          return ReadAndSplitImage<itk::Image<double,2> >(inputVolume,outputVolume,transform);
          break;
        default:
          return 1; // shouldn never happen
        }
      break;
    case 3:
      switch(componentType)
        {
        case itk::ImageIOBase::UCHAR:
          return ReadAndSplitImage<itk::Image<unsigned char,3> >(inputVolume,outputVolume,transform);
          break;
        case itk::ImageIOBase::CHAR:
          return ReadAndSplitImage<itk::Image<char,3> >(inputVolume,outputVolume,transform);
          break;
        case itk::ImageIOBase::USHORT:
          return ReadAndSplitImage<itk::Image<unsigned short,3> >(inputVolume,outputVolume,transform);
          break;
        case itk::ImageIOBase::SHORT:
          return ReadAndSplitImage<itk::Image<short,3> >(inputVolume,outputVolume,transform);
          break;
        case itk::ImageIOBase::UINT:
          return ReadAndSplitImage<itk::Image<unsigned int,3> >(inputVolume,outputVolume,transform);
          break;
        case itk::ImageIOBase::INT:
          return ReadAndSplitImage<itk::Image<int,3> >(inputVolume,outputVolume,transform);
          break;
        case itk::ImageIOBase::ULONG:
          return ReadAndSplitImage<itk::Image<unsigned long,3> >(inputVolume,outputVolume,transform);
          break;
        case itk::ImageIOBase::LONG:
          return ReadAndSplitImage<itk::Image<long,3> >(inputVolume,outputVolume,transform);
          break;
        case itk::ImageIOBase::FLOAT:
          return ReadAndSplitImage<itk::Image<float,3> >(inputVolume,outputVolume,transform);
          break;
        case itk::ImageIOBase::DOUBLE:
          return ReadAndSplitImage<itk::Image<double,3> >(inputVolume,outputVolume,transform);
          break;
        default:
          return 1; // shouldn never happen
        }
      break;
    default:
      break;
    }
  return 1;
}