# Lab 4: Call your model using the SDK in DataScience Notebook
## Introduction

In this lab, you will call the Key Value Detection model through OCI preview SDK within a DataScience notebook.

Estimated Time: 40 minutes


### Objectives

In this lab, you will:

* Get to know how to create a Datascience notebook in OCI console
* Learn to setup API Signing Key and Config File
* Call the model in notebook through OCI preview SDK

### Prerequisites

Before you can start using Data Science, your tenancy administrator should set up the following networking, dynamic group, and policies.
* Create a VCN and subnets using Virtual Cloud Networks > Start VCN Wizard > VCN with Internet Connectivity option. The Networking Quickstart option automatically creates the necessary private subnet with a NAT gateway.
* Create a dynamic group with the following matching rule: ALL { resource.type = 'datasciencenotebooksession' }
* Create policies in the root compartment with the following statements:

  * Service Policies
  ```
  allow service datascience to use virtual-network-family in tenancy
  ```
  * Non-Administrator User Policies
  ```
  allow group <data-scientists> to use virtual-network-family in tenancy
  ```
  ```
  allow group <data-scientists> to manage data-science-family in tenancy
  ```
  where data-scientists represents the name of your user group.

  * Dynamic Group Policies
  ```
  allow dynamic-group <dynamic-group> to manage data-science-family in tenancy
  ```
  where dynamic-group represents the name of your dynamic group.

## Task 1: Navigate to the Data Science Notebook Session

* Using the Burger Menu on the top left corner, navigate to _Analytics and AI menu_ and click it, and then select **"Data Science item"** under _Machine Learning_. 
![](./custom_kv_labs/images/notebook1.PNG)
* Select the Compartment in which want to create your project. 
* Click **"Create Project"** to create a new project. 
![](./custom_kv_labs/images/notebook2.PNG)
* Enter name and click **"Create Button"**.
![](./custom_kv_labs/images/notebook3.PNG)
* Click **"Create Notebook Session"** to create a new Notebook session. 
![](./custom_kv_labs/images/notebook4.PNG)
* Enter Notebook details: Select a name. Choose Intel Skylake VM.Standard2.2 as the shape. Set block storage to 50 GB. Select the subnet with Internet connectivity. (Select private subnet if you have use VCN Wizard to create VCN)
![](./custom_kv_labs/images/notebook5.PNG)
* The Notebook Session VM will be created. This might take a few minutes. When created you will see a screen like the following. Open the notebook session that was provisioned.
![](./custom_kv_labs/images/notebook6.PNG)

## Task 2: Setup API Signing Key and Config File

Generate an API signing key pair

* Open the Profile menu (User menu icon) and click User Settings.
![](./custom_kv_labs/images/api1.PNG)
* Navigate to API Key and then Click **"Add API Key"**.
![](./custom_kv_labs/images/api2.PNG)
* In the dialog, select **"Generate API Key Pair"**. Click Download Private Key, save the key file and then click Add.
![](./custom_kv_labs/images/api3.PNG)
* Copy the values shown on the console.
![](./custom_kv_labs/images/api4.PNG)
* Create a config file and paste the values copied. Replace the key_file value with the path of your generated API Key.
![](./custom_kv_labs/images/api5.PNG)
  The private key and config files will be utilized in the next tasks.

  To know more visit [Generating API KEY](https://docs.oracle.com/en-us/iaas/Content/API/Concepts/apisigningkey.htm) and [SDK and CLI Configuration File](https://docs.oracle.com/en-us/iaas/Content/API/Concepts/sdkconfig.htm#SDK_and_CLI_Configuration_File)

* Open the Notebook session you created in Task 1. Open the Terminal by clicking the Terminal icon in the Launcher Tab.
* In the terminal, create a .oci directory in the Data Science notebook session.
  ```
  mkdir ~/.oci
  ```
* Upload the Config file and the Private Key to the Notebook Session by clicking on the Upload Files Icon you just created.

  In the terminal, move those files to the .oci folder.
  ```
  mv <path of the config file> ~/.oci/
  ```
  ```
  mv <path of the private key> ~/.oci/
  ```
![](./custom_kv_labs/images/api6.PNG)


## Task 3: Call your model

* Download and upload the file [Key_Value_Detection.ipynb](./custom_kv_labs/notebooks/Key_Value_Detection.ipynb) in the notebook
![](./custom_kv_labs/images/sdk.PNG)
* Open the Notebook that you've just uploaded. Now go through each of the cells and run them one by one. You can click Shift+Enter on each cell to run the code in the cell.

This notebook demonstrate how you can productively use the Key Value Detection Feature of Document service through notebook

## **Summary**

Congratulations! </br>
In this lab you have learnt how to access the key value detection model through OCI preview SDK.

You may now **proceed to the next lab**.

[Proceed to the next section](./lab-05-postman.md).
