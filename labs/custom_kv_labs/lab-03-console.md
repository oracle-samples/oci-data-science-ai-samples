# Lab 3: Call your model in the OCI Console
## Introduction

In this lab, you will use the OCI Console invoke the model created in previous lab.

Estimated Time: 10 minutes


### Objectives

In this workshop, you will:

* Get to know how to create a call the key value detection model created in [previous lab](./lab-02-model_training.md)

## Task: Invoke model through OCI console
* Once the model is active, select **"Analyze"** under _Resources_ header on the left hand side of the console
* Click on **"Select to change output location"** to give output location. From the dropdown list give the compartment.
* Select UsabilityTest bucket under Output object storage location. Give a prefix, where the output documents have to stored
![](./images/console1.png)
* Once the output location is given, call your model by uploading the document from local
![](./images/console2.png)

## **Summary**

Congratulations! </br>
In this lab you have learnt how to call a trained model through OCI console.

You may now **proceed to the next lab**.

[Proceed to the next section](./lab-04-notebook_sdk.md).
