# Lab 4.5 - Executing a Training Job

## Introduction

[Data Science Jobs](https://docs.oracle.com/en-us/iaas/data-science/using/jobs-about.htm) enable custom tasks because you can apply any use case you have, such as data preparation, model training, hyperparameter tuning, batch inference, and so on.

Using jobs, you can:

* Run machine learning (ML) or data science tasks outside of your notebook sessions in JupyterLab.
* Operationalize discrete data science and machine learning tasks as reusable runnable operations.
* Automate your typical MLOps or CI/CD pipeline.
* Execute batches or workloads triggered by events or actions.
* Batch, mini batch, or distributed batch job inference.

After the steps are completed, you can automate the process of data exploration, model training, deploying and testing using jobs. A single change in the data preparation or model training, experiments with hyperparameter tunings could be run as Job and independently tested.

Jobs are two parts, a job and a job run:

### Job
A job is a template that describes the task. It contains elements like the job artifact that is immutable and can't be modified after it's uploaded to a job. Also, the job contains information about the Compute shapes the job runs on, logging options, block storage, and other options. You can add environment variables or CLI arguments to jobs to be unique or similar for all your future job runs. You can override these variables and arguments in job runs.

You can edit the Compute shape in the job and between job runs. For example, if you notice that you want to execute a job run on more powerful shape, you can edit the job Compute shape, and then start a new job run.

### Job Run
A job run is the actual job processor. In each job run, you can override some of the job configuration, and most importantly the environment variables and CLI arguments. You can have the same job with several sequentially or simultaneously started job runs with different parameters. For example, you could experiment with how the same model training process performs by providing different hyperparameters.

Estimated Lab Time: 10 minutes

## Objectives
In this lab, you will:
* Use ADS to define a Data Science Job 
* Execute and monitor the progress of your Job Run. 

## Prerequisites

* Successful completion of Labs 0, 1, 2, and 3. 

## STEP 1: Execute the notebook `1.5-(optional)-model-training-job.ipynb`

A notebook has been prepared containing all the necessary Python code to train and save the same machine learning model as in lab 3 but this time we will run the training script as a Data Science Job. 

  1. In the file browser, navigate to the directory **/home/datascience/lab/labs/MLSummit21/Notebooks/**. This directory was created in Lab 1 when you unzip this repository in your notebook session. 

  1. Open the notebook **1.5-(optional)-model-training-job.ipynb** (double-click on it). A new tab opens in the workspace on the right.

     Notice in the upper right corner of the notebook tab, it displays the name of the conda environment being used by this notebook. Confirm that the name you see the slugname of the TensorFlow conda environment (`tensorflow27_p37_cpu_v1`)
  
  ![](./images/confirm-kernel.png)

  1. Now you will work in the notebook. Scroll through each cell and read the explanations. When you encounter a `code` cell, execute it (using **shift + enter**) and view the results. For executable cells, the ""[ ]"" changes to a "[\*]" while executing, then a number when complete "[1]". (If you run short on time, you can use the *Run* menu to run the remaining cells and the review the results.) 

**Congratulations! You are now ready to proceed to the next lab.**
