# ![oowbanner](https://objectstorage.us-ashburn-1.oraclecloud.com/p/Hybywve1ppjSVxMZpUu2PU1R1p6CAvY9FDrv6gJPpOM/n/bigdatadatasciencelarge/b/hosted-datascience-docs/o/oracle-cloud-infrastructure.png)

# Overview

In this simple example, we will use a convolutional neural network (CNN) to classify speech commands. We will show how one can use 
the **Oracle Cloud Infrastructure Data Science service** to perform data preparation, model training with Keras, and deployment of the model as an Oracle Function. 

## Instructions and Example Steps

* From your notebook session environment, either `git clone` this repo into `/home/datascience/` or drag-and-drop a zip archive of this repo into the JupyterLab interface. 

## Overview 

The demo is in three parts:

* In the first part, we explore audio data and the necessary data transformations we need to apply to the data before training the neural network. Refer to the Jupyter notebook : `notebooks/1-intro-to-audio-data.ipynb`. **Make sure you run this notebook. We also pull the dataset from OCI Object Storage as one of the first steps in the notebook.** 

* In the second part, we train the CNN model using Keras. This is done in notebook `notebooks/2-cnn-model-with-keras.ipynb`

* In the last part, you test the model Function endpoint you deployed to Oracle Functions with pre-recorded audio clips. The Instructions are stored in `notebooks/3-testing-model-deployment.ipynb`. 

## Dataset 

Throughout this demo, we use the [Speech Commands Dataset (Warden 2018)](https://arxiv.org/abs/1804.03209). You have two options to dowload the raw dataset for this demo: 
* from Oracle Cloud Infrastructure Object Storage by running the first notebook `1-intro-to-audio-data.ipynb`
* from its original location [http://download.tensorflow.org/data/speech_commands_v0.01.tar.gz](http://download.tensorflow.org/data/speech_commands_v0.01.tar.gz) 

Alternatively, you can use the pre-processed and transformed dataset we use in `notebooks/2-cnn-model-with-keras.ipynb` to train the model. This dataset has been serialized and can be found in this repo (`data/processed_data.pkl`). Instructions on how to load the data can be found in `notebooks/2-cnn-model-with-keras.ipynb`. 

## Installation Instructions 

These notebooks were intended to be run on the OCI Data Science service. We install additional Python libraries 
in notebook `1-intro-to-audio-data.ipynb`. The libraries are listed in ``requirements.txt`` : 

```
pip install -r requirements.txt
```
