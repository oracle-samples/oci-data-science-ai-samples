# Offline Video Service

## Introduction

Vision is a serverless, multi-tenant service, accessible using the Console, SDK or over REST APIs. 
Offline Video Service is a part of Vision Service which enables you to upload videos to detect and classify objects and text in the given video. You can use out of the box pre-trained models and also customize the models to suite a specific domain.

*Estimated Workshop Time*: 100 minutes

### Objectives

In this livelab, you will:

* Get familiar with the OCI Preview SDK, Datascience Notebook and be able to demo key video features with it.

### Pretrained Models

#### 1. Video Object Detection 
Detects and locates the objects in a video. Video Object Detection gives the bounding box, confidence values and the frame details of the detected objects for each frame along with video segment details where the object is present.
#### 2. Video Label Detection
Classifies the video segments based on the objects within the video. Video Label Detection gives a pre-determined labels for a video segment with confidence and video segment details.
#### 3. Video Text Detection
Detects and recognizes text in a video. Video Text Detection gives the bounding box, confidence values and the frame details of the detected text for each frame along with video segment details where the text is present.
#### 4. Video Face Detection
Detects the face present in the video. Video Face Detection gives the bounding box, confidence values and the frame details of the detected face for each frame along with video segment details where the face is present.

### Custom Models
Offline Video Service custom models enables you to customize Video Object Detection and Label Detection with your own data of images and thus analyze the video.

#### 1. Video Object Detection 
Enables you to analyze video with the custom object detection model which is created using images.

#### 2. Video Label Detection
Enables you to analyze video with the custom label detection model which is created using images.


### Prerequisites
* An Oracle Free Tier, or Paid Cloud Account
* Additional prerequisites (cloud services) are mentioned per lab
* Familiar with OCI Policy.
* Familiar with Python programming for SDK usage is recommended.
* Request access to OCI Vision + review policy requirements


[Proceed to the next section](./lab-00-policies.md).
