# Lab 2: Train a Custom Key Value Extraction model in OCI Document Understanding
## Introduction

In this lab, you will use the OCI Console to create and train a model in OCI Document Understanding.

Estimated Time: 10 minutes


### Objectives

In this workshop, you will:

* Get to know how to create a Project. 
* Learn to create and train a Key Value extraction model.

## Task 1: Create a Project 

A Project is a way to organize multiple models in the same workspace. It is the first step to start.

* Log into OCI Cloud Console. Using the Burger Menu on the top left corner, navigate to _Analytics and AI menu_ and click it, and then select **"Document Understanding Service"** item under _AI services_.

![](./images/project1.png)

* Once here, select Projects under **"Custom Models"** header on the left-hand side of the console.

![](./images/project2.png)

* Provide any name to your project(for e.g: Usability_YourName). Once the details are entered click the Create Button. If the project is successfully created it will show up in the projects panel.  

![](./images/project3.png)


## Task 2: Train a new custom model

Now that you’ve created a project, go back to the Project details page to create your custom model with the following guidelines:

* Select **"Models"** under the _Resources_ header on the left-hand side of the console and click on **"Create Model"**.

![](./images/model1.png)

* Train a key value extraction model.
* For Training Dataset:
  * If Lab 1 is not done: select **"Create a New Dataset"**. This will drive you to OCI Data Labeling service page, where you can follow [Lab 1](./lab-01-dataset_creation.md) to create a dataset.
  * If Lab 1 is done: select **"Choose existing dataset"**. Give "Data Labelling Service" as the data source and from the dropdown list select the dataset created in Lab 1.

![](./images/model2.png)

* In the _"train model"_ step, Use any name for the custom model you want(for e.g: Test_YourName).
* Add a description of the model(optional).
* Select **"Recommended training"** in the training duration section. 

![](./images/model3.png)

* Review the details and click on submit.

## **Summary**

Congratulations! </br>
In this lab, you have learnt how to create and train a custom key value extraction model.

You may now **proceed to the next lab**.

[Proceed to the next section](./lab-03-console.md).
