# Pi Day Hands-On Lab
# Be an AI Wizard: No ML magic required

## Lab 0: Introduction

This lab is built for use as a workshop at the Oracle Pi Day event in March 2022. It uses Oracle Cloud Infrastructure (OCI) Vision service to show how AI services can be used with applications. The workshop guides the user to run a safety application that that looks for persons not wearing hardhats in images of industrial scenes.

OCI Vision is a serverless, multi-tenant cloud service, accessible using the Console, over REST APIs, or via programming language SDKs. It detects and classifies objects in images. Batches of images can be processed using asynchronous API endpoints. OCI Vision features include both document AI for document-centric images and image analysis for object and scene-based images.

### 1. Image Analysis

* Object Detection is an image analysis feature that detects and locates the objects in an image. For example, if the image is of a living room, Vision locates the objects therein, such as a chair, a sofa, and a TV. It then draws bounding boxes around the objects and identifies them. It can also be used for visual anomaly detection by training it to detect anomalous objects in images.
* Image Classification is an image analysis feature used to identify scene-based features and objects in an image.
* Text Recognition (also known as Optical Character Recognition) means Vision can detect and recognize text in an image. Vision draws bounding boxes around the printed or hand-written text it locates in an image, and digitizes the text.

### 2. Document AI

* Text Recognition (also known as Optical Character Recognition) means Vision can detect and recognize text in a document. Vision draws bounding boxes around the printed or hand-written text it locates in an image, and digitizes the text.
* Document Classification determines the type of document, such as a tax form, an invoice, or a receipt.
* Language Classification detects the language of document based on visual features.
* Table Extraction extracts content in tabular format, maintaining row/column relationships of cells.
* Key Value Extraction (Receipts) can be used to identify values for predefined keys in a receipt. For example, if a receipt includes a merchant name, merchant address, or merchant phone number, Vision can identify these values and return them as a key value pair.

Document AI is a key building block for scenarios like business process automation (also called RPA for Robotic Process Automation), automated receipt processing, semantic search, and the automatic extraction of information from unstructured content like scanned documents.

Custom model training tailors base models (through transfer learning approaches) to make deep learning models tuned to the training data. Model selection, resource planning, and deployment are all managed by Vision.

*Estimated Workshop Time*: 90 minutes

### Objectives

In this workshop, you will:

* Configure an OCI tenancy for OCI Vision
* Get familiar with the OCI Console and exercise OCI Vision features with it
* Learn how to use REST API to communicate with OCI Vision endpoints
* Execute a sample application that processes a batch of images using object detection
* Learn how to train an image classification or object detection model through the OCI console

### Prerequisites
  - None
  - Familiar with Python programming is recommended.

[Proceed to the next lab](./Lab-1-tenancy-access.md).
