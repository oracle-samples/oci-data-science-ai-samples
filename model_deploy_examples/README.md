# Model Deployment Examples

## Overview

This is a list of model examples based on machine learning frameworks that are used for making a deployment.
1. LightGBM: LightGBM, LightGBM_ONNX
2. Pytorch: PyTorch_ResNet152
3. Sklearn: SklearnLR, Random_Forest
4. Tensorflow: TF_ResNet152, TFKeras
5. XGBoost: XGBoost, XGBoost_ONNX

Each model directory contains a trained model, score.py file and runtime.yaml file at minimum (more details on [how to prepare a model](https://docs.oracle.com/en-us/iaas/data-science/using/models-prepare.htm)).
Each model can be deployed and invoked with the OCI Python SDK.

### Instructions 

* You can use either resource principals or the config and key authn mechanism to create or invoke the model. More details on setup and prequisites can be found [here](https://docs.oracle.com/en-us/iaas/Content/API/Concepts/devguidesetupprereq.htm)
* Assume you have an oci config file that contains information about user, fingerprint, tenancy, region, and key_file in ~/.oci/config. 
* The Python package "requests" is required to install to make a prediction using model deployment url [here](https://pypi.org/project/requests/)
  
### Steps
  1. Add compartment_id and project_id into file model_deployment_config.json.
  2. Modify/check model_id after uploading a model successfully and possible update other model deployment configuration in file model_deployment_config.json to make a deployment. 
  3. Model deployment configuration contains some default values as below:
    * instance_shape_name = "VM.Standard2.1"
    * instance_count = 1
    * bandwidth_mbps = 10
  4. Optionally you can set up logging for model deployment, and you need to update log_group_id, access_log_id and predict_log_id in file model_deployment_config.json.

#### To create and upload a model artifact into model catalog

*python3 upload_model.py --model_file_name={model file name: the folder that contains the model, score.py and runtime.yaml files}*
 
* An optional argument to provide oci config file path:
    * *--oci_config_file={oci config file path}*

Example: *python3 upload_model.py --model_file_name=LightGBM* --oci_config_file=~/.oci/config
#### To create a model deployment:

*python3 deploy_model.py --oci_config_file={oci config file path}*

* An optional argument to provide oci config file path:
    * *--oci_config_file={oci config file path}*

More information can be found at [creating a model deployment](https://docs.oracle.com/en-us/iaas/data-science/using/model_dep_create.htm)  

#### To make inference from deployed model

*python3 call_prediction.py --model_deployment_id={model deployment ocid}*

* Optional arguments 
    * *--oci_config_file={oci config file path}*: to provide oci config file path
    * *--input_file={test input file path for prediction}*: to provide input file path, for example --input_file=./test_inputs/LightGBM.yaml

#### To perform an end to end model deployment in a single command

*python3 run_example.py --model_file_name={model file name: the folder that contains the model, socre.py and runtime.yaml files}*

* Optional arguments
    * *--project_id={project id}*: to provide project id
    * *--compartment_id={compartment id}*: to provide a compartment id
    * *--oci_config_file={oci config file path}*: to provide oci config file path
    * *--input_file={test input file path for prediction}*: to provide input file path, for example --input_file=./test_inputs/LightGBM.yaml

Example: *python3 run_example.py --model_file_name=LightGBM* --oci_config_file=~/.oci/config --input_file=./test_inputs/LightGBM.yaml

More information can be found at [invoking a model deployment](https://docs.oracle.com/en-us/iaas/data-science/using/model-dep-invoke.htm)

#### To delete a model deployment

*python3 delete_deployment.py*

If you want to **delete a model**, you will need to delete all associated deployments first and then run:

*python3 delete_model.py*

