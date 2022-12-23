# Lab 1: Label a dataset in OCI Data Labeling Service
## Introduction

In this lab, you will use the OCI Console to create dataset in Data Labelling Service.

Estimated Time: 20 minutes


### Objectives

In this workshop, you will:

* Get to know how to create a new dataset for Key Value Extraction model 
* Label the documents in the created datset

## **Task 1:** Create a new Dataset for a Key Value Extraction Model

You will be creating a custom key value detection model for this session with documents from the [data folder](./data).

Create a new dataset with the following guidelines
### 1. Navigate to **Data Labeling Page** on OCI Console

![](./images/dataset1.PNG)

* On the Data Labeling Page, select **"Datasets"** on the left navigation menu and click on **"Create dataset"**
![](./images/dataset2.PNG)
* Name it _“Test_YourName”_
* This will be a key-value detection dataset
![](./images/dataset3.PNG)
* Choose to upload these documents as local files
![](./images/dataset4.PNG)
* Save this dataset under the bucket UsabilityTest
![](./images/dataset5.PNG)
* Upload the files that are downloaded above
![](./images/dataset6.PNG)
* You want to detect the values for **"Recipient" "Carrier Name" "Shipping ID"** and **"Trailer Number"** from these sample documents
![](./images/dataset7.PNG)
* Review and click on **"Create"**
![](./images/dataset8.PNG)
## **Task 2:** Label the documents in your Dataset

Now that your dataset is generated, begin labeling your dataset. Click on the name of the document to annotate it.

* Start labeling all the labels
![](./images/label1.PNG)
  * Recipient
![](./images/label2.PNG)
  * Carrier Name
![](./images/label3.PNG)
  * Shipping ID
![](./images/label4.PNG)
  * Trailer Number
![](./images/label5.PNG)
* Annotate all 6 documents
![](./images/label6.PNG)
![](./images/label7.PNG)
![](./images/label8.PNG)
![](./images/label9.PNG)
![](./images/label10.PNG)
![](./custom_kv_labsimages/label11.PNG)
* You can check the labelled values by clicking on Ⓢ icon
![](./images/label12.PNG)
## **Summary**

Congratulations! </br>
In this lab you have learnt how to create a dataset and how to annotate the documents in the dataset.

You may now **proceed to the next lab**.

[Proceed to the next section](./lab-02-model_training.md).
