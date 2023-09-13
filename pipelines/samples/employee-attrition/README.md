# Employee attrition pipeline sample

## description
This sample uses the "Employee attrition classification" dataset to create a model for predicting which employee is at risk for leaving based on employee data. The sample uses a pipeline to train several models and choose the best one, then deploy it to a real-time endpoint. The sample uses ADS (Accelerated Data Science) SDK to create and run the pipeline for improved developer experience.

The pipeline has the following steps:
    1. Import data, process and featurize
    1. Train 3 types of models in parallel:
        1.1. Logistic Regression classification model
        1.1. Random Forest classification model
        1.1. XGBoost classification model
    1. Evaluate the models, choose the best model based on Area Under Curve (AUC) metric and deploy the best model

## How to use
Open the [employee-attrition-pipeline-ads.ipynb](./employee-attrition-pipeline-ads.ipynb) notebook and run it.

Make sure you define the permissions in your tenancy properly.
<br/><br/>

:warning: **NOTE**: You need ADS (Accelerated Data Science) SDK version 2.8 or above to use pipelines.

To check ADS version in your environment, open a termial window and run the command: ```pip show oracle-ads```

To update ADS version in your environment, open a terminal window and run the command: ```pip install oracle-ads --upgrade```


## Dependencies
mlpipeline_data_helpers.py - helper functions to transfer data between steps

## Environment variables required
For all steps:
    DATA_LOCATION - Object storage bucket to use for temporary data transfer between steps
 
## Optional environment variables
For the data processign step (employee-attr-dataproc):
    ATTRITION_DATA_PATH - Object storage location for the attrition data. if not defined the default will be used
For the training steps (employee-attr-train-lr, employee-attr-train-rf, employee-attr-train-xgb):
    SKIP_MODEL_SAVE - to skip saving the model to the model catalog (for development phase)
For the evaluation and deployment step (employee-attr-eval-deploy):
    SKIP_MODEL_DEPLOY - to skip model deployment (for development phase)
    DONT_DELETE_MODELS - skip model deletion from the catalog (for development phase)
    CLEANUP_RESOURCES - delete the resources created during the pipeline - model deployment and model in the catalog

