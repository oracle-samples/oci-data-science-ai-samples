Model Deployment Lab
====================

This lab is a tutorial on how to create a toy model and deploy it. You create a sklearn random forest model by training it on synthetic data. You create a model artifact and save it into the Model Catalog. Then deploy the model using the Model Deployment service. This is done programmatically with the OCI Python SDK. Then a sample data set is sent to the deployed model for inference.

# Prerequisites

The notebook makes connections to other OCI resources. This is done using [resource principals](https://docs.oracle.com/en-us/iaas/Content/Functions/Tasks/functionsaccessingociresources.htm). If you have not configured your tenancy to use resource principals then you can do so using the instructions that are [here](https://docs.oracle.com/en-us/iaas/data-science/using/create-dynamic-groups.htm). Alternatively, you can use API keys. The preferred method for authentication is resource principals.

Your notebook needs internet access.

# Instructions

1. Open a Data Science Notebook session (i.e. JupyterLab).
1. Open a file terminal by clicking on File -> New -> Terminal.
1. In the terminal run the following commands:
    1. `odsc conda install -s pytorch18_p37_cpu_v1` to install the  PyTorch for CPU Python 3.7 conda.
    1. `conda activate /home/datascience/conda/pytorch18_p37_cpu_v1` to activate the conda.
    1. `pip install oci` to install the OCI Python SDK.
1. Copy the `model-deployment.ipynb` into the notebook session.
1. Open the notebook.
1. Change the notebook kernel to `Python [conda env:pytorch18_p37_cpu_v1]`.
1. Read the notebook and execute each cell.

Note:

* Read through the notebook and look for value place holders. These place holders are denoted by angle brackets surrounding some text. For example, `deployment_name = "<your-deployment-name>"`. You would replace `<your-deployment-name>` with the actual name of your deployment, such as `deployment_name = "My Test Model Deployment"`.
* By default, logs are not emitted to the Logging service. However, you can set it up yourself by creating custom logs for both predict and access logs.
