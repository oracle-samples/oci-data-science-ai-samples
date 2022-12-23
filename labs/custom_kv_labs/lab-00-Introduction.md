# Lab 0: Introduction

### Objectives
In this workshop, we will go through the end to end steps of creating a custom key-value extraction model with OCI Document Understanding. We will mainly:

* Learn how to train an KeyValue detection model through the OCI console
* Learn how to use REST API to communicate with our document service endpoints.


### Prerequisites

* Familiarity with Python
* OCI Paid Account
* Access to OCI Document Understanding preview SDK (request access here)

## Policy Setup
Before you start using OCI Document Understanding, OCI policies should be setup for allowing you to access OCI Document Understanding Service. Follow these steps to configure required policies.

### 1. Navigate to Policies
Log into OCI Cloud Console. Using the Burger Menu on the top left corner, navigate to Identity & Security and click it, and then select Policies item under Identity.

![](./images/policy1.png)

### 2. Create Policy

Click Create Policy

![](./images/policy2.png)

### 3. Set compartment to your root compartment and toggle on the manual editor
    
Configure as shown below: 

![](./images/policy3.PNG)

### 4. Create Policy to grant users Document APIs access (Required)

Add the below statement to allow all the users in your tenancy to use document understanding:
```
allow any-user to manage ai-service-document-family in tenancy
```

![](./images/policy4.PNG)

If you want to limit access to a user group, create a policy with the below statement:
```
<copy>allow group <group-name> to use ai-service-document-family in tenancy</copy>
```

### 5. Policy to access input document files in object storage (Recommended)

If your want to analyze documents stored in your tenancy's object storage bucket, add the below statement to grant object storage access permissions to the group:
```
allow group <group_in_tenancy> to use object-family in tenancy
```
    
If you want to restrict access to a specific compartment, you can use the following policy instead: 
```
allow group <group_in_tenancy> to use object-family in compartment <input_bucket_located_object_storage_compartment>
```

### 6. Policy to access output location in object storage (Required)

Document Understanding Service stores results in your tenancy's object store. Add the following policy to grant object storage access permissions to the user group who requested the analysis to documents:

```
allow group <group_in_tenancy> to manage object-family in compartment <output_bucket_located_object_storage_compartment>
```
## **Summary**

Congratulations! </br>
In this lab you have learnt how to set up your OCI Document Understanding policies.

You may now **proceed to the next lab**.

[Proceed to the next section](./lab-01-dataset_creation.md).
