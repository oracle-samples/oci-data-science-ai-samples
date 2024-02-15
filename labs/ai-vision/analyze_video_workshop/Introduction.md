# Stored Video Service

## Introduction

OCI Vision Service is a serverless, multi-tenant service, accessible using the Console, SDK, or over REST APIs. 
Stored Video Service is a part of Vision Service which enables you to upload videos to detect and classify objects and text in the given video. You can use out of the box pre-trained models and also customize the models to suit a specific domain.

*Estimated Workshop Time*: 50 minutes

### Objectives

In this livelab, you will:

* Get familiar with the OCI Preview SDK, and Data Science Notebook and be able to demo key video features with it.

### Pretrained Models

#### 1. Video Object Detection 
Detects and locates the objects in a video. Video Object Detection gives the bounding box, confidence values, and the frame details of the detected objects for each frame along with video segment details where the object is present.
#### 2. Video Label Detection
Classifies the video segments based on the objects within the video. Video Label Detection gives pre-determined labels for a video segment with confidence and video segment details.
#### 3. Video Text Detection
Detects and recognizes text in a video. Video Text Detection gives the bounding box, confidence values, and the frame details of the detected text for each frame along with video segment details where the text is present.
#### 4. Video Face Detection
Detects the face present in the video. Video Face Detection gives the bounding box, confidence, quality score, and the frame details of the detected face for each frame along with video segment details where the face is present. In addition to these Video Face Detection also has an optional parameter *isLandmarkRequired* with the default value of false, which in case of true returns facial landmarks. Facial Landmarks includes LEFT_EYE, RIGHT_EYE, NOSE_TIP, LEFT_EDGE_OF_MOUTH, RIGHT_EDGE_OF_MOUTH.

### Custom Models
Custom model training lets you tailor base models (through transfer learning approaches) to make deep learning models tuned to your data. Model selection, resource planning, and deployment are all managed by Vision. Stored Video Service allows users to analyze video through the custom models created using their data. To know more about creation of custom models refer [Vision Livelabs](https://apexapps.oracle.com/pls/apex/r/dbpm/livelabs/run-workshop?p210_wid=931&p210_wec=&session=106686822193156). Currently custom model training is supported only with data of images whereas the trained model can be inferenced for both image and video.

#### 1. Video Object Detection 
#### 2. Video Label Detection

### Prerequisites
* An Oracle Free Tier, or Paid Cloud Account.
* Additional prerequisites (cloud services) are mentioned per lab.
* Familiar with OCI Policy.
* Familiar with Python programming for SDK usage is recommended.
* Request access to OCI Vision + review policy requirements.


[Proceed to the next section](./lab-00-policies.md).