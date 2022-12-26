# Custom Key-Value Extraction Workshop

### Objectives

In this workshop, we will go through the end to end steps of creating a custom key-value extraction model with OCI Document Understanding. We will mainly:

* Learn how to train an KeyValue extraction model through the OCI console
* Learn how to use OCI console, OCI preview SDK and REST API to communicate with our document service endpoints.


### Prerequisites

* Familiarity with Python
* OCI Paid Account
* Access to OCI Document Understanding preview SDK (request access here)

The purpose of this workshop is to give you an overview of the Key Value Extraction service without going into the details and more advanced scenarios.

Follow the lab order below. It should take about 2.5-3 hours to complete the entire workshop. 

## Lab 0: Configure Document Understanding and Data Science Policies

In [Lab 0](./lab-00-policies.md) you add all the policies required for future labs

## Lab 1: Label a dataset in OCI Data Labeling Service 

[Lab 1](./lab-01-dataset_creation.md) walks you through the process of creating and labelling a Dataset. In the first part of the lab you will create a dataset under Data Labelling Service in OCI console. Further in the second part you will labels the key values for each document

## Lab 2: Train a custom key value extraction model in OCI Document Understanding

In [Lab 2](./lab-02-model_training.md) you learn how to train a key value extraction model under Document Understanding Service in OCI console

## Lab 3: Call your model in the OCI Console

In [Lab 3](./lab-03-console.md) you will call and test the model with sample input in OCI console

## Lab 4: Call your model using the SDK in DataScience Notebook

In [Lab 4](./lab-04-notebook_sdk.md) you will learn how to access the model through OCI preview SDK in Datascience Notebook session 

## Lab 5: Deploying Your Model 

In [Lab 5](./lab-05-postman.md) we will walk you through the process of calling the model through REST API call in Postman

Enjoy the workshop :) ! 

