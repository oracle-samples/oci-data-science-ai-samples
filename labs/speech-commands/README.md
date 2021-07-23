Speech Commands Lab
===================

In this lab, you create a convolutional neural network (CNN) to classify speech commands. Oracle Cloud Infrastructure (OCI) Data Science service will be used to perform data preparation, and model training. An Oracle Function is used to deploy the model.

The demo follows these steps:
1. You explore the audio data and the data transformations that are applied before training the neural network. 
1. You train a convolutional neural network (CNN) model using Keras. 
1. You test the create an Oracle Function endpoint and deploy a model to it. You then call this endpoint and assess the inferred value from the model.

# Dataset

Throughout this lab, you use the [Speech Commands Dataset (Warden 2018)](https://arxiv.org/abs/1804.03209). The raw data can be download using the instructions in `notebooks/1-intro-to-audio-data.ipynb`. This obtains the data from a publicly accessible OCI Object Storage bucket. This data is just a copy of the [original](http://download.tensorflow.org/data/speech_commands_v0.01.tar.gz) data.
The pre-processing of the data can be time-consuming. Alternatively, you can use the pre-processed and transformed dataset `data/processed_data.pkl`. This is the data set that is used in the notebook `notebooks/2-cnn-model-with-keras.ipynb` to train the model.

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
1. Copy the `notebooks` folder into the notebook session.
1. Copy the `data` folder into the notebook session.
1. Open the notebook `notebooks/1-intro-to-audio-data.ipynb`.
1. Change the notebook kernel to `Python [conda env:mlcpuv1]`.
1. Read the notebook and execute each cell.
1. Open the notebook `notebooks/2-cnn-model-with-keras.ipynb`.
1. Change the notebook kernel to `Python [conda env:mlcpuv1]`.
1. Read the notebook and execute each cell.
1. Open the notebook `notebooks/3-testing-model-deployment.ipynb`.
1. Change the notebook kernel to `Python [conda env:mlcpuv1]`.
1. Read the notebook and execute each cell.

