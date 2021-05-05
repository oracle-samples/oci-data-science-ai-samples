# X-ray Diagnostics Demo 

## Overview 

Purpose of this demo is to detect the presence/absence of pneumonia in X-ray images of the chest area. 

We're going to see how one can tackle real-world artificial intelligence problems from end to end. To do that we're going to build a complete AI pipeline to detect pneumonia based on a patient's X-ray image. Pneumonia affects about a million Americans a year and causes about 50,000 deaths, making it top ten leading cause of death. It's estimated the US will have a shortage of more than 100,000 physicians by the year 2030. AI will help fill this gap by assisting diagnosis, letting us detect pneumonia earlier, with less reliance on medical specialists.


## Demo steps

0) Start a new notebook session. Make sure your VCN/subnet gives you access to the public internet.  

1) Once you have access to the JupyterLab interface, click on "Environment Explorer". 

2) Install the "General Machine Learning" environment (v1.0). 

3) Run through the api-keys.ipynb notebook example to setup your OCI config and key files. Alternatively you can use resource principals and skip that step. **AlL notebooks are using resource principals as the authentication mechanism**. 

4) Copy the notebook/ folder content in /home/datascience/

5) Run `ChestXrays_Train.ipynb` notebook. In this notebook we train a simple CNN model with Keras on X-ray images. The data will be stored in a folder called `./data` and a model artifact will be created under `./model_artifact`. Before you prepare() the artifact, publish your conda environment. give it the name "xray-demo". Show that the environment now shows up under "Published environments". The environment can now be shared with colleagues or can be installed in a different notebook session. 

6) Go back to the console UI and confirm the creation of the new model 

7) Deploy the model as a model deployment.


