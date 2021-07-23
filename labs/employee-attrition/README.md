Employee Attrition Lab
======================

This lab uses the Oracle Cloud Infrastructure (OCI) Data Science service to create a model-based around employee attrition. You develop a machine learning model and perform all the steps to deploy the model into production. You create a machine learning model, create a Data Flow application, create a model artifact and store it in the Model Catalog. Using the console, you deploy the model and then call a REST API endpoint to perform inference operations on your model.

# Prerequisites

The notebook makes connections to other OCI resources. This is done using [resource principals](https://docs.oracle.com/en-us/iaas/Content/Functions/Tasks/functionsaccessingociresources.htm). If you have not configured your tenancy to use resource principals then you can do so using the instructions that are [here](https://docs.oracle.com/en-us/iaas/data-science/using/create-dynamic-groups.htm). Alternatively, you can use API keys but this requires you to make a few modifications to the notebook. The preferred method for authentication is resource principals.

Your notebook needs internet access.

# Instructions

 1. Open a Data Science Notebook session (i.e. JupyterLab).
 1. Open a file terminal by clicking on File -> New -> Terminal.
 1. In the terminal run the following commands:
     1. `odsc conda install -s mlcpuv1` to install the General Machine Learning for CPUs conda.
     1. `mkdir /home/datascience/dataflow`
     1. `conda activate /home/datascience/conda/mlcpuv1` to activate the conda.
     1. `pip install oci` to install the OCI Python SDK.
 1. Copy the `employee-attrition.ipynb` into the notebook session.
 1. Open the notebook.
 1. Change the notebook kernel to `Python [conda env:mlcpuv1]`.
 1. Read the notebook and execute each cell.

Note: Before you execute the "Invoke the Model HTTP Endpoint" section, ensure you have the right endpoint URI. You can obtain this information by going to the Data Science service in the console. Select the compartment where the model deployment is contained. Then select the appropriate Project. Under the Resources section select Model Deployments. You can copy the model deployment URI from the model deployment you created.
