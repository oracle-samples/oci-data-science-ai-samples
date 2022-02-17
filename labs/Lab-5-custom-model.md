# Create a custom model through the console

## Introduction
In this session, we will show you how to create a vision project, select your training data, and train a custom model.

*Estimated Time*: 15 minutes

### Objectives

In this lab, you will:
- Learn how to create vision project.
- Understand the schema for training data.
- Learn how to train an image classification or object detection model through the OCI console.

### Prerequisites
- A Free tier or paid tenancy account in OCI (Oracle Cloud Infrastructure)
- Familiar with OCI object storage to upload data.

## **Policy Setup**

Before you start using OCI Vision, your tenancy administrator should set up the following policies by following below steps:

1. Navigate to Policies

    Log into OCI Cloud Console. Using the Burger Menu on the top left corner, navigate to Identity & Security and click it, and then select Policies item under Identity.
    ![](./images/policy1.png " ")


2. Create Policy

    Click Create Policy
    ![](./images/policy2.png " ")


3. Create a new policy with the following statements:

    If you want to allow all the users in your tenancy to use vision service, create a new policy with the below statement:
    ```
    <copy>allow any-user to use ai-service-vision-family in tenancy</copy>
    ```
    ![](./images/policy3.png " ")

    If you want to limit access to a user group, create a new policy with the below statement:
    ```
    <copy>allow group <group-name> to use ai-service-vision-family in tenancy</copy>
    ```
    ![](./images/policy4.png " ")

## **Task 1:** Create a Project

A Project is a way to organize multiple models in the same workspace. It is the first step to start.

1. Log into OCI Cloud Console. Using the Burger Menu on the top left corner, navigate to Analytics and AI menu and click it, and then select Vision Service item under AI services. Clicking the Vision Service Option will navigate one to the Vision Service Console. Once here, select Projects under "Custom Models" header on the left hand side of the console.

    ![](./images/create-project1.png " ")

1. The Create Project button navigates User to a form where they can specify the compartment in which to create a Vision Project. The project we create here is named "vision_demo".

    ![](./images/create-project2.png " ")

1. Once the details are entered click the Create Button. If the project is successfully created it will show up in projects pane.  

## **Task 2:** Select Model Type

AI Vision Service supports training of an on-demand custom model for Object Detection, Image Classification, and Document Image Classification features. You can select one of these three options in the drop down.

## **Task 3:** Select Training Data

1. To train a custom model, you will need training data. There are two main options depending on if you already have an annotated dataset, or only have raw (unlabeled) images.

    ![](./images/select-training-data1.png " ")

1. **Create a New dataset**: If you do not have any annotated images (you only have raw images you'd like to train your model on), select "Create a New Dataset".

    ![](./images/select-training-data2.png " ")

    This will drive you to OCI Data Labeling service, where you can easily add labels or draw bounding boxes over your image content. To learn more about how to annotate images using OCI Data Labeling service, you can review documentation here [Adding and Editing Labels (oracle.com)](https://docs.oracle.com/en-us/iaas/data-labeling/data-labeling/using/labels.htm).

    ![](./images/select-training-data3.png " ")

1. **Choose existing dataset**: If you have an existing annotated dataset, you can select it by clicking "Choose Existing Dataset." If you've previously annotated images using OCI Data Labeling service, select that button and select the dataset file of your choice. If you have annotated your images using some 3rd party tool, you can upload that dataset file to object storage and select via the "object storage" button.

    ![](./images/select-training-data4.png " ")

## **Task 4:** Train your Custom Model

In the "train model" step, you will name your model, add a description of it, and optionally, specify a training duration.

![](./images/train-model1.png " ")

## **Task 5:** Review and Submit

In the "review" step, you can verify that all of your information is correct and go back if you want to make adjustments (on training time, for example). When you want to start training, click "submit" and this will kick of the process. You can then check on the status of your model in the project where you created it.

![](./images/train-model2.png " ")

### Congratulations on completing this lab and workshop!
