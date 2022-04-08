# Oracle ML Summit 2021 Workshop 

In this workshop, we have gone through the simple steps of building and deploying a machine learning model in OCI Data Science including:

* Create a notebook session in OCI Data Science
* Install a Conda Environment
* Build a Machine Learning Model
* Explore the features of Model Catalog
* Deploy the model
* Deactivate resources

The purpose of this workshop was to give you an overview of the OCI Data Science service without going into the details and more advanced scenarios.

Follow the lab order below. It should take about 1-1.5 hours to complete the entire workshop. Feel free to skip any step marked as **OPTIONAL** in the Labs though we recommend that you try them. 

## Lab 0: Free Tier Account and Tenancy Setup 

In [Lab 0](./lab-0-tenancy-setup.md) you sign up for the Oracle Cloud Free Tier account and you go through the steps required to setup your tenancy for OCI Data Science. You will use the Resource Manager service and the Stacks feature to automate the creation of user groups, dynamic groups, policies, networking, a project, and a notebook session. 

At the end of Lab 0, you will have a Data Science Project and Notebook Session already created. It takes a few minutes to run the Stack automation. 


## Lab 1: Creating a Notebook Session 

[Lab 1](./lab-1-notebook-setup.md) walks you through the process of creating a Notebook Session. The first part of this lab is optional if a notebook session was successfully created by the Resource Manager Data Science Stack in Lab 0. It's a good lab to go through to understand how to create a notebook session on your own. 

In the second half of Lab 1, you will copy over the content of this repository in your notebook session. 

## Lab 2: Installing a Conda Environment 

In [Lab 2](./lab-2-install-conda.md) you learn how to install a conda environment in your notebook session. The same conda environment will be used in Lab 5 for model deployment. This labs also walks you through the Environment Explorer extension available in the notebook session. 

## Lab 3: Training a Classifer on Employee Data with `scikit-learn` and ADS

In [Lab 3](./lab-3-python-model.md) you build, train, and evaluate a simple scikit-learn model to predict employee attrition. You use the [Oracle ADS Python library](https://docs.oracle.com/en-us/iaas/tools/ads-sdk/latest/index.html) to connect to Object Storage and pull data, evaluate the model, and prepare + save the model artifact to the model catalog. 

## (Optional) Lab 4: Introduction to the Model Catalog 

In [Lab 4](./lab-4-model-catalog.md) we walk you through the metadata that is available in the model catalog as well as some of the key functionalities. 

## (Optional) Lab 4.5: Executing a Training Job

IN [Lab 4.5](./lab-45-training-job.md) we walk you through the process of executing a [Data Science Job](https://docs.oracle.com/en-us/iaas/data-science/using/jobs-about.htm) from a notebook session. It is the same training script as in Lab 3. 

## Lab 5: Deploying Your Model 

In [Lab 5](./lab-5-model-deploy.md) you deploy your model as an HTTP endpoint using the Model Deployment feature of OCI Data Science. Two different approaches are shown: through the ADS library and directly in the OCI console. 

## Lab 6: Shutting Down Your Resources 

In [Lab 6](./lab-6-resources-shutdown.md) we discuss the difference between deactivating a resource like a notebook or a deployment 
and terminating a resource. You learn how to deactivate and terminate notebooks and model deployments. 

## Lab 7: Summary and Wrap Up 

In [Lab 7](./lab-7-wrap.md) we wrap up the workshop. 


Enjoy the workshop :) ! 

