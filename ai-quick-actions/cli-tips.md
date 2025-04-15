# AI Quick Actions CLI

Table of Contents:

- [Home](README.md)
- [Policies](policies/README.md)
- [Model Deployment](model-deployment-tips.md)
- [Model Evaluation](evaluation-tips.md)
- [Model Fine Tuning](fine-tuning-tips.md)
- [Model Registration](register-tips.md)

This document provides documentation on how to use ADS to create AI Quick Actions (AQUA) model deployments, fine-tune foundational models and evaluate the models.
You'll need the latest version of ADS to run these, installation instructions are available [here](https://accelerated-data-science.readthedocs.io/en/latest/user_guide/cli/quickstart.html).

# Table of Contents

- [Models](#models)
  - [List Models](#list-models)
  - [Get Model Details](#get-model-details)
  - [Register Model](#register-model)
- [Model Deployment](#model-deployment)
  - [Create Deployment](#create-model-deployment)
  - [List Model Deployments](#list-model-deployments)
  - [Get Model Deployment Details](#get-model-deployment-details)
- [Model Evaluation](#model-evaluation)
  - [Create Model Evaluation](#create-model-evaluation)
  - [List Model Evaluation](#list-model-evaluations)
  - [Get Model Evaluation Details](#get-model-evaluation-details)
- [Model Fine-Tuning](#model-fine-tuning)
  - [Create Fine-Tuned Model](#create-fine-tuned-model)

# Models

## List Models

### Description

Lists all active Aqua models within a specified compartment and/or project.  If `compartment_id` is not specified, 
the method defaults to returning the service models within the pre-configured default compartment.

### Usage

```bash
ads aqua model list [OPTIONS]
```

### Optional Parameters

`--compartment_id [str]`

The ID of the compartment in which the aqua models are available. If not provided, then it defaults to the service compartment identified by the environment variable `ODSC_MODEL_COMPARTMENT_OCID`.

`--project_id [str]`

The ID of the project in which the aqua models are available. If not provided, then it defaults to the user's project.

`--model_type [str]`

The type of model in the user compartment, which can be either FT or BASE. FT represents the Fine-Tuned models created by the user in the user's compartment. BASE models are those which are created by
the user by explicitly registering the model when model artifacts are either imported from object storage or by importing from the HuggingFace Hub.  By default, FT is selected if this value is not set. 
This filtering is only applied when `compartment_id` is also set as input.

`**kwargs`

Additional keyword arguments that can be used to filter the results for OCI list_models API. For more details on acceptable parameters, see [ListModels API](https://docs.oracle.com/iaas/api/#/en/data-science/20190101/ModelSummary/ListModels).

### Example

```bash
ads aqua model list --compartment_id ocid1.compartment.oc1..<ocid>
```

#### CLI Output

```json
{
    "compartment_id": "ocid1.compartment.oc1..<ocid>",
    "icon": "",
    "id": "ocid1.datasciencemodel.oc1.iad.<ocid>",
    "is_fine_tuned_model": false,
    "license": "llama2",
    "name": "CodeLlama-34b-Instruct-hf",
    "organization": "Meta",
    "project_id": "",
    "tags": {
        "license": "llama2",
        "task": "code_synthesis",
        "OCI_AQUA": "",
        "organization": "Meta"
    },
    "task": "code_synthesis",
    "time_created": "2024-03-13T12:34:16.959000+00:00",
    "console_link": [
        "https://cloud.oracle.com/data-science/models/ocid1.datasciencemodel.oc1.iad.<ocid>?region=us-ashburn-1"
    ],
    "search_text": "llama2,code_synthesis,,Meta",
    "ready_to_deploy": true,
    "ready_to_finetune": true,
    "ready_to_import": false,
    "nvidia_gpu_supported": true,
    "arm_cpu_supported": false,
    "model_file": "",
    "model_formats": [
        "SAFETENSORS"
    ],
    "model_card": "<model-card-readme-string>",
    "inference_container": "odsc-vllm-serving",
    "inference_container_uri": null,
    "finetuning_container": "odsc-llm-fine-tuning",
    "evaluation_container": "odsc-llm-evaluate",
    "artifact_location": "service_models/MCodeLlama-34b-Instruct-hf/123456/artifact"
}
```

## Search Model OCID by Name

### Description

Gets the OCID of an Aqua model. This OCID is required for performing an AI Quick Actions operations like
registering, deploying or fine-tuning a model.

### Usage

```bash
ADS_AQUA_LOG_LEVEL=ERROR ads aqua model get [OPTIONS]  | jq -r 'select(.name=="<model_name>") | .id'
```
The `model_name` value should match the full model name that is available in Aqua console, for example, 
`Mistral-7B-Instruct-v0.1` or `meta-llama/Llama-3.2-3B-Instruct`. For `[OPTIONS]`, check the Optional Parameters 
section of the [List Models](#list-models) API. Note that we set the logging level to `ERROR` so that the Aqua logs do not cause issues when `jq` command parses the 
CLI output. 

### Examples
#### Get Service Model OCID

These models are ready to deploy directly on the OCI Data Science platform. Some models already include the model artifacts,
whereas for some models, models need to be registered and the artifacts need to be downloaded by
the user during the registration process either via Hugging Face or make them available via Object Storage. 

```bash
ADS_AQUA_LOG_LEVEL=ERROR ads aqua model list | jq -r 'select(.name=="Mistral-7B-Instruct-v0.1") | .id'
```

#### Get User Registered Model OCID
These models are successfully registered and now are ready to be deployed or fine-tuned.

```bash
ADS_AQUA_LOG_LEVEL=ERROR ads aqua model list --compartment_id $PROJECT_COMPARTMENT_OCID --model_type BASE | jq -r 'select(.name=="meta-llama/Meta-Llama-3.1-8B-Instruct") | .id'
```

#### Get Fine-Tuned Model OCID
These models are fine-tuned and now are ready to be deployed.
```bash
ADS_AQUA_LOG_LEVEL=ERROR ads aqua model list --compartment_id $PROJECT_COMPARTMENT_OCID --model_type FT | jq -r 'select(.name=="tunedModel_google/gemma-2b-it_20241206") | .id'
```

## Get Model Details

### Description

Gets the information of an Aqua model.

### Usage

```bash
ads aqua model get [OPTIONS]
```

### Required Parameters

`--model_id [str]`

The OCID of the Aqua model.

### Example

```bash
ads aqua model get --model_id ocid1.datasciencemodel.oc1.iad.<ocid>
```

#### CLI Output

```json
{
  "compartment_id": "ocid1.compartment.oc1..<ocid>",
  "icon": "",
  "id": "ocid1.datasciencemodel.oc1.iad.<ocid>",
  "is_fine_tuned_model": false,
  "license": "Apache 2.0",
  "name": "Mistral-7B-Instruct-v0.1",
  "organization": "Mistral AI",
  "project_id": "ocid1.datascienceproject.oc1.iad.<ocid>",
  "tags": {
    "license": "Apache 2.0",
    "task": "text_generation",
    "OCI_AQUA": "",
    "organization": "Mistral AI"
  },
  "task": "text_generation",
  "time_created": "2024-02-27T14:08:15.564000+00:00",
  "console_link": [
    "https://cloud.oracle.com/data-science/models/ocid1.datasciencemodel.oc1.iad.<ocid>?region=us-ashburn-1"
  ],
  "search_text": "The Mistral-7B-Instruct-v0.1 Large Language Model (LLM) is a instruct fine-tuned version of the Mistral-7B-v0.1 generative text model using a variety of publicly available conversation datasets. Apache 2.0,text_generation,,Mistral AI",
  "ready_to_deploy": true,
  "ready_to_finetune": true,
  "ready_to_import": false,
  "nvidia_gpu_supported": true,
  "arm_cpu_supported": false,
  "model_file": "",
  "model_formats": [
      "SAFETENSORS"
  ],
  "model_card": "<model-card-readme-string>",
  "inference_container": "odsc-vllm-serving",
  "inference_container_uri": null,
  "finetuning_container": "odsc-llm-fine-tuning",
  "evaluation_container": "odsc-llm-evaluate",
  "artifact_location": "service_models/Mistral-7B-Instruct-v0.1/123456/artifact"
}
```

## Register Model

### Description

Import the model from object storage or HuggingFace Hub and registers as Model in Data Science Model catalog as an Aqua Model.
These models do not have artifacts, and the user is expected to download the artifact from HuggingFace Hub or have the model
artifacts available in an object storage location.

### Usage

```bash
ads aqua model register [OPTIONS]
```

### Required Parameters

`--model [str]`

The OCID of the Aqua model that is marked as `Ready to Register`. These models are tested and certified to be working on Aqua components, and comes with the requisite defaults for
deployment and fine-tuning. 
The `model` parameter also accepts model name as it appears on HuggingFace Hub. In this case, the artifacts will be
downloaded from the Hub and will be associated with the model. <br>
Example: `--model ocid1.datasciencemodel.oc1.<region>.<ocid>` or `--model intfloat/e5-mistral-7b-instruct`


`--os_path [str]`

The dataset path where the artifacts will be downloaded or are already present. Must be an object storage path. <br>
Example: `oci://<bucket>@<namespace>/path/to/the/dataset`

`--inference_container [str]`

Associates the default inference container to the model being registered. The options currently
supported are one of `{'odsc-vllm-serving', 'odsc-tgi-serving', 'odsc-llama-cpp-serving' and 'odsc-tei-serving}'`. 
If registering models marked as `Ready to Register`, the default is already set and can be changed later on during model deployment.


### Optional Parameters

`--download_from_hf [bool]`

If set to `True`, the expectation is that the model artifacts will be downloaded from HuggingFace Hub. If set to `False`, the `os_path` should have
the model artifacts already downloaded. Default is set to `True`.

`--local_dir [str]`

If specified, makes a copy of the artifacts in local directory.

`--finetuning_container [str]`

Associates the default inference container to the model being registered. Currently, only
`odsc-llm-fine-tuning` is supported.

`--compartment_id [str]`

The compartment OCID where model is to be created. If not provided, then it defaults to user's compartment.

`--project_id [str]`

The project OCID where model is to be created. If not provided, then it defaults to user's project.

`--model_file [str]`

The model file name for registering GGUF models. If the file is inside a folder within the artifact location, then folder
prefix should be added as well. This parameter is only required for GGUF models.

Example: `Phi-3-mini-4k-instruct-fp16.gguf` or `gguf/Phi-3-mini-4k-instruct-fp16.gguf`


`--inference_container_uri [str]`

The URI of the inference container associated with the model being registered. This is available for 
models that will be registered and deployed using Bring Your Own Container (BYOC) approach.

Example: `iad.ocir.io/<your_tenancy>/<your_image>:<tag>`

`--defined_tags`

The defined tags to be added for the registered model. 

Example: `{"defined-tag-namespace-1":{"tag-key-1":"tag-value-1","tag-key-2":"tag-value-2"},"defined-tag-namespace-2":{"sample-tag-key":"sample-tag-value"}}`

`--freeform_tags`

The freeform tags to be added for the registered model.

Example: `{"key1":"value1","key2":"value2"}`


### Example

```bash
ads aqua model register \
  --model mistralai/Mistral-7B-Instruct-v0.1 \
  --os_path oci://<bucket>@<namespace>/<prefix> \
  --download_from_hf True \
  --inference_container odsc-vllm-serving \
  --finetuning_container odsc-llm-fine-tuning \
  --defined_tags '{"defined-tag-namespace-1":{"tag-key-1":"tag-value-1","tag-key-2":"tag-value-2"}}' \
  --freeform_tags '{"key1":"value1","key2":"value2"}'
```

#### CLI Output

```json
{                                                                                                                                                                                                                 
    "compartment_id": "ocid1.compartment.oc1..<ocid>",
    "icon": "",
    "id": "ocid1.datasciencemodel.oc1.iad.<ocid>",
    "is_fine_tuned_model": false,
    "license": "Apache 2.0",
    "name": "mistralai/Mistral-7B-Instruct-v0.1",
    "organization": "Mistral AI",
    "project_id": "ocid1.datascienceproject.oc1.iad.<ocid>",
    "tags": {
        "license": "Apache 2.0",
        "task": "text_generation",
        "OCI_AQUA": "active",
        "organization": "Mistral AI",
        "ready_to_fine_tune": "true"
    },
    "task": "text_generation",
    "time_created": "2024-02-27 14:08:15.564000+00:00",
    "console_link": "https://cloud.oracle.com/data-science/models/ocid1.datasciencemodel.oc1.iad.<ocid>?region=us-ashburn-1",
    "search_text": "The Mistral-7B-Instruct-v0.1 Large Language Model (LLM) is a instruct fine-tuned version of the Mistral-7B-v0.1 generative text model using a variety of publicly available conversation datasets. Apache 2.0,text_generation,active,Mistral AI,true",
    "ready_to_deploy": true,
    "ready_to_finetune": true,
    "ready_to_import": false,
    "nvidia_gpu_supported": true,
    "arm_cpu_supported": false,
    "model_file": "",
    "model_formats": [
        "SAFETENSORS"
    ],
    "model_card": "---\nlicense: apache-2.0\npipeline_tag: text-generation\ntags:\n- finetuned\ninference:\n  parameters:\n    temperature: 0.7\n---\n\n# Model Card for Mistral-7B-Instruct-v0.1\n\nThe Mistral-7B-Instruct-v0.1 Large Language Model (LLM) is a instruct fine-tuned version of the [Mistral-7B-v0.1](https://huggingface.co/mistralai/Mistral-7B-v0.1) generative text model using a variety of publicly available conversation datasets.",
    "inference_container": "odsc-vllm-serving",
    "inference_container_uri": null,
    "finetuning_container": "odsc-llm-fine-tuning",
    "evaluation_container": "odsc-llm-evaluate",
    "artifact_location": "service_models/Mistral-7B-Instruct-v0.1/3dc28cf/artifact"
}
```

# Model Deployment

## Create Model Deployment

### Description

Creates a new Aqua model deployment.

### Usage

```bash
ads aqua deployment create [OPTIONS]
```

### Required Parameters

`--model_id [str]`

The model OCID to deploy.

`--instance_shape [str]`

The shape of the instance used for model deployment. <br>
Example: ` VM.GPU.A10.1, VM.GPU.A10.2, BM.GPU.A10.4, BM.GPU4.8, BM.GPU.A100-v2.8`.

`--display_name [str]`

The name of model deployment.


### Optional Parameters

`--compartment_id [str]`

The compartment OCID where model deployment is to be created. If not provided, then it defaults to user's compartment.

`--project_id [str]`

The project OCID where model deployment is to be created. If not provided, then it defaults to user's project.

`--description [str]`

The description of the model deployment. Defaults to None.

`--instance_count [int]`

The number of instance used for model deployment. Defaults to 1.

`--log_group_id [str]`

The oci logging group id. The access log and predict log share the same log group.

`--access_log_id [str]`

The access log OCID for the access logs. Check [model deployment logging](https://docs.oracle.com/en-us/iaas/data-science/using/model_dep_using_logging.htm) for more details.

`--predict_log_id [str]`

The predict log OCID for the predict logs. Check [model deployment logging](https://docs.oracle.com/en-us/iaas/data-science/using/model_dep_using_logging.htm) for more details.

`--web_concurrency [int]`

The number of worker processes/threads to handle incoming requests.

`--server_port [int]`

The server port for docker container image. Defaults to 8080.

`--health_check_port [int]`

The health check port for docker container image. Defaults to 8080.

`--env_var [dict]`

Environment variable for the model deployment, defaults to None.

`--container_family [str]`

The image family of model deployment container runtime. Currently, one of
`{'odsc-vllm-serving', 'odsc-tgi-serving', 'odsc-llama-cpp-serving' and 'odsc-tei-serving}'` is supported. The default value
is already set at the model level, but user can choose to override.


`--memory_in_gbs [float]`

The memory in gbs for the shape selected, applicable only for Flex shape supported for deploying GGUF models.

`--ocpus [float]`

The ocpu count for the shape selected, applicable only for Flex shape supported for deploying GGUF models.


`--model_file [str]`

The model file name for GGUF models. If the file is inside a folder within the artifact location, then folder
prefix should be added as well. This parameter is only required for GGUF models. The default value
is already set at the model level, but user can choose to override.

`--private_endpoint_id [str]`

The private endpoint id of model deployment.

`--container_image_uri [str]`

The URI of the inference container associated with the model being registered. This is available for 
models that will be registered and deployed using Bring Your Own Container (BYOC) approach.

`--cmd_var [List[str]]`

The cmd of model deployment container runtime. This is available for 
models that will be registered and deployed using Bring Your Own Container (BYOC) approach.

### Example

```bash
ads aqua deployment create \
  --model_id "ocid1.datasciencemodel.oc1.iad.<ocid>" \
  --instance_shape "VM.GPU.A10.1" \
  --display_name "modelDeployment_Mistral-7B-v0.1 FT"
```

#### CLI Output

```json
{
    "id": "ocid1.datasciencemodeldeployment.oc1.iad.<ocid>",
    "display_name": "modelDeployment_Mistral-7B-v0.1 FT",
    "aqua_service_model": false,
    "aqua_model_name": "Mistral-7B-v0.1 FT Model EXT",
    "state": "ACTIVE",
    "description": null,
    "created_on": "2024-10-30 04:58:16.931000+00:00",
    "created_by": "ocid1.datasciencenotebooksession.oc1.iad.<ocid>",
    "endpoint": "https://modeldeployment.us-ashburn-1.oci.oc-test.com/ocid1.datasciencemodeldeployment.oc1.iad.<ocid>",
    "private_endpoint_id": "",
    "console_link": "https://cloud.oracle.com/data-science/model-deployments/ocid1.datasciencemodeldeployment.oc1.iad.<ocid>?region=us-ashburn-1",
    "lifecycle_details": "Model Deployment is Active.",
    "shape_info": {
        "instance_shape": "VM.GPU.A10.1",
        "instance_count": 1,
        "ocpus": null,
        "memory_in_gbs": null
    },
    "tags": {
        "aqua_fine_tuned_model": "ocid1.datasciencemodel.oc1.iad.<ocid>#Mistral-7B-v0.1",
        "OCI_AQUA": "active",
        "aqua_model_name": "Mistral-7B-v0.1 FT Model EXT"
    },
    "environment_variables": {
        "PARAMS": "--served-model-name odsc-llm --seed 42  --max-model-len 4096",
        "MODEL_DEPLOY_PREDICT_ENDPOINT": "/v1/completions",
        "BASE_MODEL": "service_models/Mistral-7B-v0.1/78814a9/artifact",
        "FT_MODEL": "ui-test/ocid1.datasciencejob.oc1.iad.<ocid>",
        "MODEL_DEPLOY_ENABLE_STREAMING": "true",
        "PORT": "8080",
        "HEALTH_CHECK_PORT": "8080"
    },
    "cmd": [],
    "log_group": {
        "id": "ocid1.loggroup.oc1.iad.<ocid>",
        "name": "aqua-model-deploy-log-group",
        "url": "https://cloud.oracle.com/logging/log-groups/ocid1.loggroup.oc1.iad.<ocid>?region=us-ashburn-1"
    },
    "log": {
        "id": "ocid1.log.oc1.iad.<ocid>",
        "name": "aqua-model-deploy-logs",
        "url": "https://cloud.oracle.com/logging/search?searchQuery=search \"ocid1.compartment.oc1..<ocid>/ocid1.loggroup.oc1.iad.<ocid>/ocid1.log.oc1.iad.<ocid>\" | source='ocid1.datasciencemodeldeployment.oc1.iad.<ocid>' | sort by datetime desc&regions=us-ashburn-1"
    }
}
```
#### With Model Deployment settings
The start up parameters for the container is passed using environment variable called PARAMS. Here is an example to set the max-model-len.
Refer to the vllm docs to find the parameter to setup 
```bash
ads aqua deployment create \
    --model_id "ocid1.datasciencemodel.oc1.iad.<ocid>"  \
    --instance_shape "VM.GPU.A10.1" \
    --display_name "Lora Deployment" \
    --project-id $PROJECT_OCID  \
    --log_group_id "ocid1.loggroup.oc1.iad.<ocid>" \
    --access_log_id "ocid1.log.oc1.iad.<ocid>" \
    --predict_log_id "ocid1.log.oc1.iad.<ocid>" \
    --env_var '{"MODEL_DEPLOY_PREDICT_ENDPOINT": "/v1/chat/completions", "PARAMS": "--max-model-len 6000 "}'
   
```
## List Model Deployments

### Description

Lists all Aqua model deployments within a specified compartment and/or project.

### Usage

```bash
ads aqua deployment list [OPTIONS]
```

### Optional Parameters

`--compartment_id [text]`

The ID of the compartment in which the aqua model deployments are available. If not provided, then it defaults to the user's compartment.

`**kwargs`

Additional keyword arguments that can be used to filter the results for OCI list_model_deployments API. For more details on acceptable parameters, see [List Model Deployments API](https://docs.oracle.com/iaas/api/#/en/data-science/20190101/ModelDeploymentSummary/ListModelDeployments).


### Example

```bash
ads aqua deployment list
```

#### CLI Output

```
{
    "id": "ocid1.datasciencemodeldeployment.oc1.iad.<ocid>",
    "display_name": "modelDeployment_Mistral-7B-v0.1 FT",
    "aqua_service_model": false,
    "aqua_model_name": "Mistral-7B-v0.1 FT Model EXT",
    "state": "ACTIVE",
    "description": null,
    "created_on": "2024-10-30 04:58:16.931000+00:00",
    "created_by": "ocid1.datasciencenotebooksession.oc1.iad.<ocid>",
    "endpoint": "https://modeldeployment.us-ashburn-1.oci.oc-test.com/ocid1.datasciencemodeldeployment.oc1.iad.<ocid>",
    "private_endpoint_id": "",
    "console_link": "https://cloud.oracle.com/data-science/model-deployments/ocid1.datasciencemodeldeployment.oc1.iad.<ocid>?region=us-ashburn-1",
    "lifecycle_details": "Model Deployment is Active.",
    "shape_info": {
        "instance_shape": "VM.GPU.A10.1",
        "instance_count": 1,
        "ocpus": null,
        "memory_in_gbs": null
    },
    "tags": {
        "aqua_fine_tuned_model": "ocid1.datasciencemodel.oc1.iad.<ocid>#Mistral-7B-v0.1",
        "OCI_AQUA": "active",
        "aqua_model_name": "Mistral-7B-v0.1 FT Model EXT"
    },
    "environment_variables": {
        "PARAMS": "--served-model-name odsc-llm --seed 42  --max-model-len 4096",
        "MODEL_DEPLOY_PREDICT_ENDPOINT": "/v1/completions",
        "BASE_MODEL": "service_models/Mistral-7B-v0.1/78814a9/artifact",
        "FT_MODEL": "ui-test/ocid1.datasciencejob.oc1.iad.<ocid>",
        "MODEL_DEPLOY_ENABLE_STREAMING": "true",
        "PORT": "8080",
        "HEALTH_CHECK_PORT": "8080"
    },
    "cmd": [],
    "log_group": {
        "id": "ocid1.loggroup.oc1.iad.<ocid>",
        "name": "aqua-model-deploy-log-group",
        "url": "https://cloud.oracle.com/logging/log-groups/ocid1.loggroup.oc1.iad.<ocid>?region=us-ashburn-1"
    },
    "log": {
        "id": "ocid1.log.oc1.iad.<ocid>",
        "name": "aqua-model-deploy-logs",
        "url": "https://cloud.oracle.com/logging/search?searchQuery=search \"ocid1.compartment.oc1..<ocid>/ocid1.loggroup.oc1.iad.<ocid>/ocid1.log.oc1.iad.<ocid>\" | source='ocid1.datasciencemodeldeployment.oc1.iad.<ocid>' | sort by datetime desc&regions=us-ashburn-1"
    }
}
...
...
...
```

## Search Model Deployment OCID by Name

### Description

Gets the OCID of an Aqua model deployment. This OCID is required for performing evaluation of the Aqua model
or to perform inference.

### Usage

```bash
ADS_AQUA_LOG_LEVEL=ERROR ads aqua deployment get [OPTIONS]  | jq -r 'select(<field>=="<field_value>") | .id'
```
The `field_value` value should match the either full model name or model deployment name. For `[OPTIONS]`, check the Optional Parameters 
section of the [List Model Deployments](#list-model-deployments) API. Note that we set the logging level to `ERROR` so that the Aqua logs do not cause issues when `jq` command parses the 
CLI output. 

### Examples
#### Get Service Model Deployment OCID

These deployments are ready to be evaluated (if active). 

To get the OCID using model deployment name, use:

```bash
ADS_AQUA_LOG_LEVEL=ERROR ads aqua deployment list | jq -r 'select(.display_name=="gemma-2b-it-md") | .id'
```

To get the OCID using model name, use:
```bash
ADS_AQUA_LOG_LEVEL=ERROR ads aqua deployment list | jq -r 'select(.aqua_model_name=="google/gemma-2b-it") | .id'
```

## Get Model Deployment Details

### Description

Gets the information of an Aqua model deployment.

### Usage

```bash
ads aqua deployment get [OPTIONS]
```

### Required Parameters

`--model_deployment_id [str]`

The OCID of the Aqua model deployment.

`**kwargs`

Additional keyword arguments that can be used to filter the results for OCI get_model_deployment API. For more details on acceptable parameters, see [Get Model Deployment API](https://docs.oracle.com/iaas/api/#/en/data-science/20190101/ModelDeployment/GetModelDeployment).

### Example

```bash
ads aqua deployment get --model_deployment_id "ocid1.datasciencemodeldeployment.oc1.iad.<ocid>"
```

#### CLI Output

```json
{
    "id": "ocid1.datasciencemodeldeployment.oc1.iad.<ocid>",
    "display_name": "modelDeployment_Mistral-7B-v0.1 FT",
    "aqua_service_model": false,
    "aqua_model_name": "Mistral-7B-v0.1 FT Model EXT",
    "state": "ACTIVE",
    "description": null,
    "created_on": "2024-10-30 04:58:16.931000+00:00",
    "created_by": "ocid1.datasciencenotebooksession.oc1.iad.<ocid>",
    "endpoint": "https://modeldeployment.us-ashburn-1.oci.oc-test.com/ocid1.datasciencemodeldeployment.oc1.iad.<ocid>",
    "private_endpoint_id": "",
    "console_link": "https://cloud.oracle.com/data-science/model-deployments/ocid1.datasciencemodeldeployment.oc1.iad.<ocid>?region=us-ashburn-1",
    "lifecycle_details": "Model Deployment is Active.",
    "shape_info": {
        "instance_shape": "VM.GPU.A10.1",
        "instance_count": 1,
        "ocpus": null,
        "memory_in_gbs": null
    },
    "tags": {
        "aqua_fine_tuned_model": "ocid1.datasciencemodel.oc1.iad.<ocid>#Mistral-7B-v0.1",
        "OCI_AQUA": "active",
        "aqua_model_name": "Mistral-7B-v0.1 FT Model EXT"
    },
    "environment_variables": {
        "PARAMS": "--served-model-name odsc-llm --seed 42  --max-model-len 4096",
        "MODEL_DEPLOY_PREDICT_ENDPOINT": "/v1/completions",
        "BASE_MODEL": "service_models/Mistral-7B-v0.1/78814a9/artifact",
        "FT_MODEL": "ui-test/ocid1.datasciencejob.oc1.iad.<ocid>",
        "MODEL_DEPLOY_ENABLE_STREAMING": "true",
        "PORT": "8080",
        "HEALTH_CHECK_PORT": "8080"
    },
    "cmd": [],
    "log_group": {
        "id": "ocid1.loggroup.oc1.iad.<ocid>",
        "name": "aqua-model-deploy-log-group",
        "url": "https://cloud.oracle.com/logging/log-groups/ocid1.loggroup.oc1.iad.<ocid>?region=us-ashburn-1"
    },
    "log": {
        "id": "ocid1.log.oc1.iad.<ocid>",
        "name": "aqua-model-deploy-logs",
        "url": "https://cloud.oracle.com/logging/search?searchQuery=search \"ocid1.compartment.oc1..<ocid>/ocid1.loggroup.oc1.iad.<ocid>/ocid1.log.oc1.iad.<ocid>\" | source='ocid1.datasciencemodeldeployment.oc1.iad.<ocid>' | sort by datetime desc&regions=us-ashburn-1"
    }
}  
```

# Model Evaluation

## Create Model Evaluation

### Description

Creates a new evaluation model using an existing Aqua model deployment.

### Usage

```bash
ads aqua evaluation create [OPTIONS]
```

### Required Parameters

`--evaluation_source_id [str]`

The evaluation source id. Must be model deployment OCID.

`--evaluation_name [str]`

The name for evaluation.

`--dataset_path [str]`

The dataset path for the evaluation. Must be an object storage path. <br>
Example: `oci://<bucket>@<namespace>/path/to/the/dataset.jsonl`

`--report_path [str]`

The report path for the evaluation. Must be an object storage path. <br>
Example: `oci://<bucket>@<namespace>/report/path/`

`--model_parameters [str]`

The parameters for the evaluation. <br>
Example: `'{"max_tokens": 500, "temperature": 0.7, "top_p": 1.0, "top_k": 50}'`


`--shape_name [str]`

The shape name for the evaluation job infrastructure. <br>
Example: `VM.Standard.E3.Flex, VM.Standard.E4.Flex, VM.Standard3.Flex, VM.Optimized3.Flex`.

`--block_storage_size [int]`

The storage for the evaluation job infrastructure.

### Optional Parameters

`--compartment_id [str]`

The compartment OCID where evaluation is to be created. If not provided, then it defaults to user's compartment.

`--project_id [str]`

The project OCID where evaluation is to be created. If not provided, then it defaults to user's project.

`--evaluation_description [str]`

The description of the evaluation. Defaults to None.

`--memory_in_gbs [float]`

The memory in gbs for the flexible shape selected.

`--ocpus [float]`

The ocpu count for the shape selected.

`--experiment_id [str]`

The evaluation model version set id. If provided, evaluation model will be associated with it. Defaults to None. <br>

`--experiment_name [str]`

The evaluation model version set name. If provided, the model version set with the same name will be used if exists, otherwise a new model version set will be created with the name.

`--experiment_description [str]`

The description for the evaluation model version set.

`--log_group_id [str]`

The log group id for the evaluation job infrastructure. Defaults to None.

`--log_id [str]`

The log id for the evaluation job infrastructure. Defaults to None.

`--metrics [list]`

The metrics for the evaluation, currently BERTScore and ROGUE are supported. <br>
Example: `'[{"name": "bertscore", "args": {}}, {"name": "rouge", "args": {}}]`

`--force_overwrite [bool]`

A flag to indicate whether to force overwrite the existing evaluation file in object storage if already present. Defaults to `False`.

### Example

```bash
ads aqua evaluation create  \
  --evaluation_source_id "ocid1.datasciencemodeldeployment.oc1.iad.<ocid>" \
  --evaluation_name "test_evaluation" \
  --dataset_path "oci://<bucket>@<namespace>/path/to/the/dataset.jsonl" \
  --report_path "oci://<bucket>@<namespace>/report/path/" \
  --model_parameters '{"max_tokens": 500, "temperature": 0.7, "top_p": 1.0, "top_k": 50}' \
  --shape_name "VM.Standard.E4.Flex" --block_storage_size 50 \
  --metrics '[{"name": "bertscore", "args": {}}, {"name": "rouge", "args": {}}]
```

#### CLI Output

```json
{
    "id": "ocid1.datasciencemodeldeployment.oc1.iad.<ocid>",
    "name": "test_evaluation",
    "aqua_service_model": true,
    "state": "CREATING",
    "description": null,
    "created_on": "2024-02-03 21:21:31.952000+00:00",
    "created_by": "ocid1.user.oc1..<ocid>",
    "endpoint": "https://modeldeployment.us-ashburn-1.oci.customer-oci.com/ocid1.datasciencemodeldeployment.oc1.iad.<ocid>",
    "console_link": "https://cloud.oracle.com/data-science/model-deployments/ocid1.datasciencemodeldeployment.oc1.iad.<ocid>?region=us-ashburn-1",
    "shape_info": {
        "instance_shape": "VM.Standard.E4.Flex",
        "instance_count": 1,
        "ocpus": 1.0,
        "memory_in_gbs": 16.0
    },
    "tags": {
        "aqua_service_model": "ocid1.datasciencemodel.oc1.iad.<ocid>#Llama-2-13b",
        "OCI_AQUA": ""
    }
}
```

## List Model Evaluations

### Description

Lists all Aqua model evaluations within a specified compartment and/or project.

### Usage

```bash
ads aqua evaluation list [OPTIONS]
```

### Required Parameters

`--compartment_id [text]`

The ID of the compartment in which the aqua model evaluations are available.


### Example

```bash
ads aqua evaluation list --compartment_id ocid1.compartment.oc1..<ocid>
```

#### CLI Output

```json
{
    "id": "ocid1.datasciencemodel.oc1.iad.<ocid>",
    "name": "test-eval",
    "console_url": "https://cloud.oracle.com/data-science/models/ocid1.datasciencemodel.oc1.iad.<ocid>?region=us-ashburn-1",
    "lifecycle_state": "FAILED",
    "lifecycle_details": "",
    "time_created": "2024-03-18T00:31:28.026000+00:00",
    "tags": {
        "aqua_evaluation": "aqua_evaluation"
    },
    "experiment": {
        "id": "ocid1.datasciencemodelversionset.oc1.iad.<ocid>",
        "name": "experiment_name",
        "url": "https://cloud.oracle.com/data-science/model-version-sets/ocid1.datasciencemodelversionset.oc1.iad.<ocid>?region=us-ashburn-1"
    },
    "source": {
        "id": "ocid1.datasciencemodeldeploymentint.oc1.iad.ocid",
        "name": "mistral-classifier",
        "url": "https://cloud.oracle.com/data-science/model-deployments/ocid1.datasciencemodeldeploymentint.oc1.iad.<ocid>?region=us-ashburn-1"
    },
    "job": {
        "id": "ocid1.datasciencejobrunint.oc1.iad.<ocid>",
        "name": "test-eval",
        "url": "https://cloud.oracle.com/data-science/job-runs/ocid1.datasciencejobrunint.oc1.iad.<ocid>?region=us-ashburn-1"
    },
    "parameters": {
        "max_tokens": 500,
        "top_p": 1,
        "top_k": 50,
        "temperature": 0.7,
        "presence_penalty": 0,
        "frequency_penalty": 0,
        "stop": [],
        "shape": "VM.Standard.E3.Flex",
        "dataset_path": "oci://<bucket>@<namespace>/path/to/the/dataset.jsonl",
        "report_path": "oci://<bucket>@<namespace>/report/path"
    }
}
```

## Get Model Evaluation Details

### Description

Gets the information of an Aqua model evaluation.

### Usage

```bash
ads aqua evaluation get [OPTIONS]
```

### Required Parameters

`--eval_id [str]`

The OCID of the Aqua model evaluation.


### Example

```bash
ads aqua evaluation get --eval_id "ocid1.datasciencemodel.oc1.iad.<ocid>"
```

#### CLI Output

```json
{
    "id": "ocid1.datasciencemodel.oc1.iad.<ocid>",
    "name": "test-eval",
    "console_url": "https://cloud.oracle.com/data-science/models/ocid1.datasciencemodel.oc1.iad.<ocid>?region=us-ashburn-1",
    "lifecycle_state": "FAILED",
    "lifecycle_details": "An error occurred during the evaluation, please check the log for more information. Exit code: 1.",
    "time_created": "2024-03-18T00:06:07.994000+00:00",
    "tags": {
        "aqua_evaluation": "aqua_evaluation"
    },
    "experiment": {
        "id": "ocid1.datasciencemodelversionset.oc1.iad.<ocid>",
        "name": "experiment_name",
        "url": "https://cloud.oracle.com/data-science/model-version-sets/ocid1.datasciencemodelversionset.oc1.iad.<ocid>?region=us-ashburn-1"
    },
    "source": {
        "id": "ocid1.datasciencemodeldeploymentint.oc1.iad.<ocid>",
        "name": "mistral-classifier",
        "url": "https://cloud.oracle.com/data-science/model-deployments/ocid1.datasciencemodeldeploymentint.oc1.iad.<ocid>?region=us-ashburn-1"
    },
    "job": {
        "id": "ocid1.datasciencejobrunint.oc1.iad.<ocid>",
        "name": "test-eval",
        "url": "https://cloud.oracle.com/data-science/job-runs/ocid1.datasciencejobrunint.oc1.iad.<ocid>?region=us-ashburn-1"
    },
    "parameters": {
        "max_tokens": 500,
        "top_p": 1,
        "top_k": 50,
        "temperature": 0.7,
        "presence_penalty": 0,
        "frequency_penalty": 0,
        "stop": [],
        "shape": "VM.Standard.E3.Flex",
        "dataset_path": "oci://<bucket>@<namespace>/path/to/the/dataset.jsonl",
        "report_path": "oci://<bucket>@<namespace>/report/path"
    },
    "log_group": {
        "id": "",
        "name": null,
        "url": ""
    },
    "log": {
        "id": "",
        "name": null,
        "url": ""
    },
    "introspection": {
        "aqua_evaluate": {
            "output_report_path": {
                "key": "output_report_path",
                "category": "aqua_evaluate",
                "description": "Verify output report path.",
                "error_msg": "The destination folder does not exist or cannot be accessed for writing. Please verify that the folder exists and has the appropriate write permissions.",
                "success": false
            }
        }
    }
}
```

# Model Fine-Tuning

## Create Fine-Tuned Model

### Description

Creates a new fine-tuned model using an existing Aqua model with a user provided dataset.

### Usage

```bash
ads aqua fine_tuning create [OPTIONS]
```

### Required Parameters

`--ft_source_id [str]`

The fine-tuning source id. Must be foundational model OCID.

`--ft_name [str]`

The name for the fine-tuned model.

`--dataset_path [str]`

The dataset path for the model fine-tuning. Must be an object storage path. <br>
Example: `oci://<bucket>@<namespace>/path/to/the/dataset.jsonl`

`--report_path [str]`

The report path of the fine-tuned model. Must be an object storage path. <br>
Example: `oci://<bucket>@<namespace>/report/path/`

`--ft_parameters [dict]`

The parameters for model fine-tuning. Currently, user can configure learning rate and number of epochs. <br>
Example: `'{"epochs": 10, "learning_rate": 0.0002}'`

`--shape_name [str]`

The shape name for the model fine-tuning job infrastructure. <br>
Example: `VM.GPU.A10.1, VM.GPU.A10.2, BM.GPU.A10.4, BM.GPU4.8, BM.GPU.A100-v2.8`.

`--replica [int]`

The replica count for the model fine-tuning job runtime.

`--validation_set_size [float]`

The validation set size for fine-tuning job. Must be a float in between [0,1).


### Optional Parameters

`--compartment_id [str]`

The compartment OCID where evaluation is to be created. If not provided, then it defaults to user's compartment.

`--project_id [str]`

The project OCID where evaluation is to be created. If not provided, then it defaults to user's project.

`--ft_description [str]`

The description of the fine-tuned model. Defaults to None.

`--experiment_id [str]`

The fine-tuned model version set id. If provided, evaluation model will be associated with it. Defaults to None.

`--experiment_name [str]`

The fine-tuned model version set name. If provided, the model version set with the same name will be used if exists, otherwise a new model version set will be created with the name.

`--experiment_description [str]`

The description for the fine-tuned model version set.

`--block_storage_size [int]`

The storage for the model fine-tuning job infrastructure.

`--subnet_id [str]`

The custom egress for model fine-tuning job. Defaults to None.

`--log_group_id [str]`

The log group id for the evaluation job infrastructure. Defaults to None.

`--log_id [str]`

The log id for the evaluation job infrastructure. Defaults to None.

`--force_overwrite [bool]`

A flag to indicate whether to force overwrite the existing evaluation file in object storage if already present. Defaults to `False`.

### Example

Subnet is optional in the below command

```bash
ads aqua fine_tuning create \
  --ft_source_id "ocid1.datasciencemodel.oc1.iad.<ocid>" \
  --ft_name "Mistral-7B-Instruct-v0.1 FT" \
  --dataset_path "oci://<bucket>@<namespace>/path/to/the/dataset.jsonl" \
  --report_path "oci://<bucket>@<namespace>/report/path" \
  --ft_parameters '{"epochs": 10, "learning_rate": 0.0002}' \
  --shape_name "VM.GPU.A10.2" \
  --replica 1 \
  --validation_set_size 0.5 \
  --subnet_id "ocid1.subnet.oc1.iad.<ocid>" \
  --log_group_id "ocid1.loggroup.oc1.iad.<ocid>" \
  --log_id "ocid1.log.oc1.iad.<ocid>" \
  --experiment_id "my_sample_experiment"
```

#### CLI Output

```json
{
    "id": "ocid1.datasciencemodel.oc1.iad.<ocid>",
    "name": "Test Mistral-7B-Instruct-v0.1 FT",
    "console_url": "https://cloud.oracle.com/data-science/models/ocid1.datasciencemodel.oc1.iad.<ocid>?region=us-ashburn-1",
    "lifecycle_state": "ACCEPTED",
    "lifecycle_details": "",
    "time_created": "2024-03-18 22:59:02.748000+00:00",
    "tags": {
        "aqua_finetuning": "aqua_finetuning",
        "finetuning_job_id": "ocid1.datasciencejob.oc1.iad.<ocid>",
        "finetuning_source": "ocid1.datasciencemodel.oc1.iad.<ocid>",
        "finetuning_experiment_id": "ocid1.datasciencemodelversionset.oc1.iad.<ocid>"
    },
    "experiment": {
        "id": "ocid1.datasciencemodelversionset.oc1.iad.<ocid>",
        "name": "test_version_set",
        "url": "https://cloud.oracle.com/data-science/model-version-sets/ocid1.datasciencemodelversionset.oc1.iad.<ocid>?region=us-ashburn-1"
    },
    "source": {
        "id": "ocid1.datasciencemodel.oc1.iad.<ocid>",
        "name": "Mistral-7B-v0.1",
        "url": "https://cloud.oracle.com/data-science/models/ocid1.datasciencemodel.oc1.iad.<ocid>?region=us-ashburn-1"
    },
    "job": {
        "id": "ocid1.datasciencejob.oc1.iad.<ocid>",
        "name": "Test Mistral-7B-Instruct-v0.1 FT",
        "url": "https://cloud.oracle.com/data-science/jobs/ocid1.datasciencejob.oc1.iad.<ocid>?region=us-ashburn-1"
    },
    "parameters": {
        "epochs": 10,
        "learning_rate": 0.0002
    }
}
```

Table of Contents:

- [Home](README.md)
- [Policies](policies/README.md)
- [Model Deployment](model-deployment-tips.md)
- [Model Evaluation](evaluation-tips.md)
- [Model Fine Tuning](fine-tuning-tips.md)
- [Model Registration](register-tips.md)
