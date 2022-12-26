# Lab 1: Label a dataset in OCI Data Labeling Service
## Introduction

In this lab, you will use the OCI Console to create dataset in Data Labelling Service.

Estimated Time: 20 minutes


### Objectives

In this workshop, you will:

* Get to know how to create a new dataset for Key Value Extraction model 
* Label the documents in the created datset

## **Task 1:** Create an Object Storage Bucket (This step is optional in case the bucket is already created)

* Using the Burger Menu on the top left corner, navigate to Storage and select **"Buckets"** under Object Storage section.

![](./images/bucket1.png)

* Then, Select Compartment from the left dropdown menu.
* Next click Create Bucket.

![](./images/bucket2.png)

* Next, fill out the dialog box:

  * Bucket Name: Provide a name of your choice(e.g: UsabilityTest)
  * Storage Tier: STANDARD

* Then click Create

![](./images/bucket3.png)

## **Task 2:** Create a new Dataset for a Key Value Extraction Model

You will be creating a custom key value extraction model for this session with documents from the [data folder](./data).

Create a new dataset with the following guidelines
* Navigate to **Data Labeling Page** on OCI Console

![](./images/dataset1.png)

* On the Data Labeling Page, select **"Datasets"** on the left navigation menu and click on **"Create dataset"**

![](./images/dataset2.png)

* Under the name section, provide any name to your dataset. For example: "Test_XYZ"
* This will be a key-value extraction dataset

![](./images/dataset3.png)

* Choose to upload these documents as local files

![](./images/dataset4.png)

* Choose the destination-bucket(created in Task1) to save the dataset
 Uploaded dataset from local will automatically get saved inside selected bucket along with all the existing data.

![](./images/dataset5.png)

* Upload the files to be labelled in the section **"Selected files"** shown below

![](./images/dataset6.png)

* We want to extract the values for **"Recipient" "Carrier Name" "Shipping ID"** and **"Trailer Number"** from the given sample documents(You can give labels depending on the type of data you create dataset with)

![](./images/dataset7.png)

* Review and click on **"Create"**

![](./images/dataset8.png)

## **Task 3:** Label the documents in your Dataset

Now that your dataset is generated, begin labelling your dataset. Select the document which you want to annotate by clicking on its name.

![](./images/label14.png)

* Start labelling all the labels

![](./images/label1.png)

* Click on the specific word to label it

![](./images/label15.png)

* To label multiple words with same key, annotate it multiple times by clicking on each word

![](./images/label13.png)

  1. Recipient

![](./images/label2.png)

  2. Carrier Name

![](./images/label3.png)

  3. Shipping ID

![](./images/label4.png)

  4. Trailer Number

![](./images/label5.png)

* You can validate the labelled values by going to the summary dashboard by clicking on Ⓢ icon

![](./images/label12.png)

* Annotate all 6 documents

![](./images/label6.png)

![](./images/label7.png)

![](./images/label8.png)

![](./images/label9.png)

![](./images/label10.png)

![](./images/label11.png)

## **Summary**

Congratulations! </br>
In this lab you have learnt how to create a dataset and how to annotate document for key value extraction.

You may now **proceed to the next lab**.

[Proceed to the next section](./lab-02-model_training.md).
