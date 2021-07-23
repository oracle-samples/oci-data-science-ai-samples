X-ray Diagnostics Lab
=====================

In this lab, you use the Oracle Cloud Infrastructure (OCI) Data Science service to build a machine learning model to classify chest x-ray images. Each image is of a patient that is suspected of having pneumonia. The machine learning model will classifies an image as having the presence or absence of the disease.

The lab will demonstrate how one can tackle real-world artificial intelligence problems from end to end. To do this, you will build a complete machine learning pipeline to detect pneumonia. Pneumonia affects about a million Americans a year and causes about 50,000 deaths. This makes it one of the top ten leading causes of death in the United States. It's estimated the US will have a shortage of more than 100,000 physicians by the year 2030. Machine learning will help fill this gap by assisting diagnosis, letting us detect pneumonia earlier, with less reliance on medical specialists.

# Prerequisites

The notebook makes connections to other OCI resources. This is done using [resource principals](https://docs.oracle.com/en-us/iaas/Content/Functions/Tasks/functionsaccessingociresources.htm). If you have not configured your tenancy to use resource principals then you can do so using the instructions that are [here](https://docs.oracle.com/en-us/iaas/data-science/using/create-dynamic-groups.htm). Alternatively, you can use API keys. The preferred method for authentication is resource principals.

Your notebook needs internet access.

# Instructions

1. Open a Data Science Notebook session (i.e. JupyterLab).
1. Open a file terminal by clicking on File -> New -> Terminal.
1. In the terminal run the following commands:
1. `odsc conda install -s mlcpuv1` to install the General Machine Learning for CPUs conda.
    1. `conda activate /home/datascience/conda/mlcpuv1` to activate the conda.
    1. `pip install oci` to install the OCI Python SDK.
    1. `pip install scikit-image`
    1. `pip install keras`
    1. `pip install tensorflow`
1. Copy the `notebooks` folder into the notebook session.
1. Copy the `data` folder into the notebook session.
1. Open the notebook `notebook/ChestXrays_Train.ipynb`.
1. Change the notebook kernel to `Python [conda env:mlcpuv1]`.
1. Read the notebook and execute each cell. The data will be stored in a folder called `./data` and a model artifact is created under `./model_artifact`.
1. Before you `prepare()` the artifact, publish your conda environment. In the terminal, run the command `odsc conda publish -s xray-demo`.
1. To confirm that the conda was published, click on File -> New Launcher and look for the conda environment.
1. Complete the rest of the notebook.
1. Open the notebook `notebook/ChestXrays_Validate.ipynb`.
1. Change the notebook kernel to `Python [conda env:mlcpuv1]`.
1. Read the notebook and execute each cell.


