## Notebook Examples

The following notebook examples serve as tutorials to prepare and save different model artifacts and then deploy them as well.

1. [linear_regression_generic.ipynb](linear_regression_generic.ipynb)
    * This notebook will provide an example to prepare and save an sklearn model artifact using ADS generic method and deploy the model as an HTTP endpoint
    
1. [pytorch_pretrained.ipynb](pytorch_pretrained.ipynb)
    * This notebook will provide an example to prepare and save a pytorch model artifact using ADS, will publish a conda environment, and deploy the model as an HTTP endpoint.
    
1. [saving_model_oci_python_sdk.ipynb](saving_model_oci_python_sdk.ipynb)
    * This example notebook demonstrates creating and uploading a XGBoost binary logisitic-based model, with metadata and schema, to the model catalog v2.0.
    
1. [simple-model-deployment.ipynb](simple-model-deployment.ipynb)
    * This example notebook demonstrates to deploy a sklearn random forest classifier as an HTTP endpoint using Model Deployment.
    
1. [uploading_larger_artifact_oci_python_sdk.ipynb](uploading_larger_artifact_oci_python_sdk.ipynb)
    * This example notebook demonstrates simple solution for OCI Python SDK which allows data scientists to upload larger model artifacts and eliminate the timeout error that is experienced by most folks when the artifact is large. It shows end-to-end steps from setting up the configuration till uploading the model artifact.
    
1. [uploading_larger_artifact_oracle_ads.ipynb](uploading_larger_artifact_oracle_ads.ipynb)
    * This example notebook demonstrates simple solution for Oracle ADS Library which allows data scientists to upload larger model artifacts and eliminate the timeout error that is experienced by most folks when the artifact is large. It shows end-to-end steps from setting up the configuration till uploading the model artifact.
    
1. [xgboost_onnx.ipynb](xboost_onnx.ipynb)
    * This example notebook demonstrates how to prepare and save an xgboost model artifact using the ADSModel `prepare()` method and deploy the model as an HTTP endpoint.
    