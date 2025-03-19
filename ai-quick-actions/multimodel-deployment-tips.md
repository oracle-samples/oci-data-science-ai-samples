# **AI Quick Actions MultiModel Deployment (Available through CLI only)**

# Table of Contents

- [Models](#models)
- [MultiModel Deployment](#multimodel-deployment)
  - [List Available Shapes](#list-available-shapes)
  - [Get MultiModel Configuration](#get-multimodel-configuration)
  - [Create Deployment](#create-multimodel-deployment)
  - [List Model Deployments](#list-multimodel-deployments)
  - [Get Model Deployment Details](#get-multimodel-deployment-details)
- [MultiModel Inferencing](#multimodel-inferencing)
- [MultiModel Evaluation](#multimodel-evaluation)
  - [Create Model Evaluation](#create-model-evaluations)


# Introduction to MultiModel Deployment and Serving

MultiModel inference and serving refers to efficiently hosting and managing multiple large language models simultaneously to serve inference requests using shared resources. The Data Science server has prebuilt **vLLM service container** that make deploying and serving multiple large language model on **single GPU Compute shape** very easy, simplifying the deployment process and reducing operational complexity. This container comes with preinstalled [**LiteLLM proxy server**]https://docs.litellm.ai/docs/simple_proxy) which routes requests to the appropriate model, ensuring seamless prediction.

**Multi-Model Deployment is currently in beta and is only available through the CLI. At this time, only base service LLM models are supported, and fine-tuned/registered models cannot be deployed.**

This document provides documentation on how to use ADS CLI to create MultiModel deployment using AI Quick Actions (AQUA) model deployments, and evaluate the models. you'll need the latest version of ADS to run these, installation instructions are available [here](https://accelerated-data-science.readthedocs.io/en/latest/user_guide/cli/quickstart.html).


# Models

First step in process is to get the OCIDs of the desired base service LLM AQUA models, which are required to initiate the MultiModel deployment process. Refer to [AQUA CLI tips](cli-tips.md) for detailed instructions on how to obtain the OCIDs of base service LLM AQUA models.

# MultiModel Deployment


## List Available Shapes

### Description

Lists the avilable **Compute Shapes** with basic information .

### Usage

```bash
ads aqua deployment list_shapes
```
### Example
```bash
ads aqua deployment list_shapes
```
##### CLI Output

```json
    {
        "core_count": 64,
        "memory_in_gbs": 1024,
        "name": "BM.GPU.A10.4",
        "shape_series": "NVIDIA_GPU",
        "gpu_specs": {
            "gpu_memory_in_gbs": 96,
            "gpu_count": 4,
            "gpu_type": "A10"
        }
    }
    {
        "core_count": 112,
        "memory_in_gbs": 1024,
        "name": "BM.GPU.L40S-NC.4",
        "shape_series": "NVIDIA_GPU",
        "gpu_specs": {
            "gpu_memory_in_gbs": 192,
            "gpu_count": 4,
            "gpu_type": "L40S"
        }
    }
    {
        "core_count": 15,
        "memory_in_gbs": 240,
        "name": "VM.GPU.A10.1",
        "shape_series": "NVIDIA_GPU",
        "gpu_specs": {
            "gpu_memory_in_gbs": 24,
            "gpu_count": 1,
            "gpu_type": "A10"
        }
    }
    {
        "core_count": 30,
        "memory_in_gbs": 480,
        "name": "VM.GPU.A10.2",
        "shape_series": "NVIDIA_GPU",
        "gpu_specs": {
            "gpu_memory_in_gbs": 48,
            "gpu_count": 2,
            "gpu_type": "A10"
        }
    }

```

## Get MultiModel Configuration

### Description

Retrieves the deployment configuration for multiple base Aqua service models and calculates the GPU allocations for all compatible shapes.

### Usage

```bash
ads aqua deployment get_multimodel_deployment_config [OPTIONS]
```

### Required Parameters

`--model_ids  [list]`

A list of OCIDs for the Aqua models <br>
Example: `["ocid1.datasciencemodel.oc1.iad...","ocid1.datasciencemodel.oc1.iad...."]`

### Optional Parameters

`--primary_model_id [str]`

The OCID of the primary Aqua model. If provided, GPU allocation will prioritize this model. Otherwise, GPUs will be evenly allocated. <br>

For example, there is one compatible shape "BM.GPU.H100.8" for three models A, B, C, and each model has a gpu count as below:

A - BM.GPU.H100.8 - 1, 2, 4, 8
B - BM.GPU.H100.8 - 1, 2, 4, 8
C - BM.GPU.H100.8 - 1, 2, 4, 8

If no primary model is provided, the gpu allocation for A, B, C could be [2, 4, 2], [2, 2, 4] or [4, 2, 2]
If B is the primary model, the gpu allocation is [2, 4, 2] as B always gets the maximum gpu count.

`**kwargs`

compartment_id: str The compartment OCID to retrieve the model deployment shapes.

### Example

```bash
ads aqua deployment get_multimodel_deployment_config --model_ids '["ocid1.datasciencemodel.oc1.iad.<ocid1>","ocid1.datasciencemodel.oc1.iad.<ocid2>"]'

```

##### CLI Output

```json
{
    "deployment_config": {
        "ocid1.datasciencemodel.oc1.iad.<ocid1>": {
            "shape": [
                "VM.GPU.A10.1",
                "VM.GPU.A10.2"
            ],
            "configuration": {
                "VM.GPU.A10.1": {
                    "parameters": {
                        "VLLM_PARAMS": "--max-model-len 4096"
                    },
                    "multi_model_deployment": [],
                    "shape_info": {
                        "configs": [],
                        "type": ""
                    }
                },
                "VM.GPU.A10.2": {
                    "parameters": {},
                    "multi_model_deployment": [
                        {
                            "gpu_count": 1,
                            "parameters": {
                                "VLLM_PARAMS": "--max-model-len 4096"
                            }
                        }
                    ],
                    "shape_info": {
                        "configs": [],
                        "type": ""
                    }
                }
            }
        },
        "ocid1.datasciencemodel.oc1.iad.<ocid2>": {
            "shape": [
                "VM.GPU.A10.1",
                "VM.GPU.A10.2",
                "BM.GPU.A10.4",
            ],
            "configuration": {
                "VM.GPU.A10.1": {
                    "parameters": {
                        "VLLM_PARAMS": "--max-model-len 4096"
                    },
                    "multi_model_deployment": [],
                    "shape_info": {
                        "configs": [],
                        "type": ""
                    }
                },
                "VM.GPU.A10.2": {
                    "parameters": {
                        "VLLM_PARAMS": "--max-model-len 8192"
                    },
                    "multi_model_deployment": [
                        {
                            "gpu_count": 1,
                            "parameters": {
                                "VLLM_PARAMS": "--max-model-len 4096"
                            }
                        }
                    ],
                    "shape_info": {
                        "configs": [],
                        "type": ""
                    }
                },
                "BM.GPU.A10.4": {
                    "parameters": {},
                    "multi_model_deployment": [
                        {
                            "gpu_count": 1,
                            "parameters": {
                                "VLLM_PARAMS": "--max-model-len 4096"
                            }
                        },
                        {
                            "gpu_count": 2,
                            "parameters": {
                                "VLLM_PARAMS": "--max-model-len 8192"
                            }
                        }
                    ],
                    "shape_info": {
                        "configs": [],
                        "type": ""
                    }
                }
            }
        }
    },
    "gpu_allocation": {
        "VM.GPU.A10.2": {
            "models": [
                {
                    "ocid": "ocid1.datasciencemodel.oc1.iad.<ocid1>",
                    "gpu_count": 1
                },
                {
                    "ocid": "ocid1.datasciencemodel.oc1.iad.<ocid2>",
                    "gpu_count": 1
                }
            ],
            "total_gpus_available": 2
        }
    },
    "error_message": null
}
```

## Create MultiModel Deployment

Only **base service LLM models** are supported for MultiModel Deployment. All selected models will run on the same **GPU shape**, sharing the available compute resources. Make sure to choose a shape that meets the needs of all models in your deployment using [MultiModel Configuration command](#get-multimodel-configuration)


### Description

Creates a new Aqua MultiModel deployment.

### Usage

```bash
ads aqua deployment create [OPTIONS]
```

### Required Parameters

`--models [str]`

The String representation of a JSON array, where each object defines a model’s OCID and the number of GPUs assigned to it. The gpu count should always be a **power of two (e.g., 1, 2, 4, 8)**. <br>
Example: `'[{"model_id":"<model_ocid>", "gpu_count":1},{"model_id":"<model_ocid>", "gpu_count":1}]'` for  `VM.GPU.A10.2` shape


`--instance_shape [str]`

The shape (GPU) of the instance used for model deployment. <br>
Example: `VM.GPU.A10.2, BM.GPU.A10.4, BM.GPU4.8, BM.GPU.A100-v2.8`.

`--display_name [str]`

The name of model deployment.

`--container_image_uri [str]`

The URI of the inference container associated with the model being registered. In case of MultiModel, the value is vLLM container URI.

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

`--private_endpoint_id [str]`

The private endpoint id of model deployment.


### Example

#### Create MultiModel deployment with `/v1/completions`

```bash
ads aqua deployment create --container_image_uri "dsmc://odsc-vllm-serving:0.6.4.post1.2" --models '[{"model_id":"ocid1.log.oc1.iad.<ocid>", "gpu_count":1},{"model_id":"ocid1.log.oc1.iad.<ocid>", "gpu_count":1}]' --instance_shape "VM.GPU.A10.2" --display_name "modelDeployment_multmodel_model1_model2"
```

##### CLI Output

```json
{
    "id": "ocid1.datasciencemodeldeployment.oc1.iad.<ocid>",
    "display_name": "Multi model deployment of Mistral-7B-v0.1 and falcon-7b on A10.2",
    "aqua_service_model": false,
    "model_id": "ocid1.datasciencemodel.oc1.<ocid>",
    "models": [
        {
            "model_id": "ocid1.datasciencemodel.oc1.iad.<ocid>",
            "model_name": "mistralai/Mistral-7B-v0.1",
            "gpu_count": 1,
            "env_var": {}
        },
        {
            "model_id": "ocid1.datasciencemodel.oc1.iad.<ocid>",
            "model_name": "tiiuae/falcon-7b",
            "gpu_count": 1,
            "env_var": {}
        }
    ],
    "aqua_model_name": "",
    "state": "CREATING",
    "description": null,
    "created_on": "2025-03-10 19:09:40.793000+00:00",
    "created_by": "ocid1.user.oc1..<ocid>",
    "endpoint": "https://modeldeployment.us-ashburn-1.oci.customer-oci.com/ocid1.datasciencemodeldeployment.oc1.iad.<ocid>",
    "private_endpoint_id": null,
    "console_link": "https://cloud.oracle.com/data-science/model-deployments/ocid1.datasciencemodeldeployment.oc1.iad.<ocid>",
    "lifecycle_details": null,
    "shape_info": {
        "instance_shape": "VM.GPU.A10.2",
        "instance_count": 1,
        "ocpus": null,
        "memory_in_gbs": null
    },
    "tags": {
        "aqua_model_id": "ocid1.datasciencemodel.oc1.iad.<ocid>",
        "aqua_multimodel": "true",
        "OCI_AQUA": "active"
    },
    "environment_variables": {
        "MODEL_DEPLOY_PREDICT_ENDPOINT": "/v1/completions",
        "MULTI_MODEL_CONFIG": "{\"models\": [{\"params\": \"--served-model-name mistralai/Mistral-7B-v0.1 --seed 42 --tensor-parallel-size 1 --max-model-len 4096\", \"model_path\": \"service_models/Mistral-7B-v0.1/78814a9/artifact\"}, {\"params\": \"--served-model-name tiiuae/falcon-7b --seed 42 --tensor-parallel-size 1 --trust-remote-code\", \"model_path\": \"service_models/falcon-7b/f779652/artifact\"}]}",
        "MODEL_DEPLOY_ENABLE_STREAMING": "true",
```

#### Create MultiModel deployment with `/v1/chat/completions`

```bash
ads aqua deployment create --container_image_uri "dsmc://odsc-vllm-serving:0.6.4.post1.2" --models '[{"model_id":"ocid1.log.oc1.iad.<ocid>", "gpu_count":1},{"model_id":"ocid1.log.oc1.iad.<ocid>", "gpu_count":1}]' --env-var '{"MODEL_DEPLOY_PREDICT_ENDPOINT":"/v1/chat/completions"}' --instance_shape "VM.GPU.A10.2" --display_name "modelDeployment_multmodel_model1_model2"
```

##### CLI Output

```json
{
    "id": "ocid1.datasciencemodeldeployment.oc1.iad.<ocid>",
    "display_name": "Multi model deployment of Mistral-7B-v0.1 and falcon-7b on A10.2",
    "aqua_service_model": false,
    "model_id": "ocid1.datasciencemodel.oc1.iad.<ocid>",
    "models": [
        {
            "model_id": "ocid1.datasciencemodel.oc1.iad.<ocid>",
            "model_name": "mistralai/Mistral-7B-v0.1",
            "gpu_count": 1,
            "env_var": {}
        },
        {
            "model_id": "ocid1.datasciencemodel.oc1.iad.<ocid>",
            "model_name": "tiiuae/falcon-7b",
            "gpu_count": 1,
            "env_var": {}
        }
    ],
    "aqua_model_name": "",
    "state": "CREATING",
    "description": null,
    "created_on": "2025-03-10 19:09:40.793000+00:00",
    "created_by": "ocid1.user.oc1..<ocid>",
    "endpoint": "https://modeldeployment.us-ashburn-1.oci.customer-oci.com/ocid1.datasciencemodeldeployment.oc1.iad.<ocid>",
    "private_endpoint_id": null,
    "console_link": "https://cloud.oracle.com/data-science/model-deployments/ocid1.datasciencemodeldeployment.oc1.iad.<ocid>",
    "lifecycle_details": null,
    "shape_info": {
        "instance_shape": "VM.GPU.A10.2",
        "instance_count": 1,
        "ocpus": null,
        "memory_in_gbs": null
    },
    "tags": {
        "aqua_model_id": "ocid1.datasciencemodel.oc1.<ocid>",
        "aqua_multimodel": "true",
        "OCI_AQUA": "active"
    },
    "environment_variables": {
        "MODEL_DEPLOY_PREDICT_ENDPOINT": "/v1/chat/completions",
        "MULTI_MODEL_CONFIG": "{\"models\": [{\"params\": \"--served-model-name mistralai/Mistral-7B-v0.1 --seed 42 --tensor-parallel-size 1 --max-model-len 4096\", \"model_path\": \"service_models/Mistral-7B-v0.1/78814a9/artifact\"}, {\"params\": \"--served-model-name tiiuae/falcon-7b --seed 42 --tensor-parallel-size 1 --trust-remote-code\", \"model_path\": \"service_models/falcon-7b/f779652/artifact\"}]}",
        "MODEL_DEPLOY_ENABLE_STREAMING": "true",
```


## List MultiModel Deployments

### Description

Lists all AQUA deployments (both MultiModel and single model) within a specified compartment and/or project, along with their associated tags.

### Usage

```bash
ads aqua deployment list [OPTIONS]
```

### Optional Parameters

`--compartment_id [text]`

The ID of the compartment in which the aqua deployments(both MultiModel and single model) are available. If not provided, then it defaults to the user's compartment.

`**kwargs`

Additional keyword arguments that can be used to filter the results for OCI list_model_deployments API. For more details on acceptable parameters, see [List Model Deployments API](https://docs.oracle.com/iaas/api/#/en/data-science/20190101/ModelDeploymentSummary/ListModelDeployments).


### Example

```bash
ads aqua deployment list
```

#### CLI Output

```json
{
    "id": "ocid1.datasciencemodeldeployment.oc1.iad.<ocid>",
    "display_name": "Multi model deployment of Mistral-7B-v0.1 and falcon-7b on A10.2",
    "aqua_service_model": false,
    "model_id": "ocid1.datasciencemodel.oc1.iad.<ocid>",
    "models": [],
    "aqua_model_name": "",
    "state": "ACTIVE",
    "description": null,
    "created_on": "2025-03-10 19:09:40.793000+00:00",
    "created_by": "ocid1.user.oc1..<ocid>",
    "endpoint": "https://modeldeployment.us-ashburn-1.oci.customer-oci.com/ocid1.datasciencemodeldeployment.oc1.iad.<ocid>",
    "private_endpoint_id": null,
    "console_link": "https://cloud.oracle.com/data-science/model-deployments/ocid1.datasciencemodeldeployment.oc1.iad.<ocid>",
    "lifecycle_details": "",
    "shape_info": {
        "instance_shape": "VM.GPU.A10.2",
        "instance_count": 1,
        "ocpus": null,
        "memory_in_gbs": null
    },
    "tags": {
        "aqua_model_id": "ocid1.datasciencemodel.oc1.iad.<ocid>",
        "aqua_multimodel": "true",
        "OCI_AQUA": "active"
    },
    "environment_variables": {
        "MODEL_DEPLOY_PREDICT_ENDPOINT": "/v1/chat/completions",
        "MULTI_MODEL_CONFIG": "{\"models\": [{\"params\": \"--served-model-name mistralai/Mistral-7B-v0.1 --seed 42 --tensor-parallel-size 1 --max-model-len 4096\", \"model_path\": \"service_models/Mistral-7B-v0.1/78814a9/artifact\"}, {\"params\": \"--served-model-name tiiuae/falcon-7b --seed 42 --tensor-parallel-size 1 --trust-remote-code\", \"model_path\": \"service_models/falcon-7b/f779652/artifact\"}]}",
        "MODEL_DEPLOY_ENABLE_STREAMING": "true",
        "PORT": "8080",
        "HEALTH_CHECK_PORT": "8080"
    },
    "cmd": []
}
...
...
...
```
MultiModel deployment will have  tag `"aqua_multimodel": "true",` associated with them.

## Search MultiModel Deployment OCID by Name

### Description

Gets the OCID of an Aqua MultiModel deployment. This OCID is required to perform an evaluation or to run inference.

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

## Get MultiModel Deployment Details

### Description

Gets the information of an Aqua MultiModel deployment.

### Usage

```bash
ads aqua deployment get [OPTIONS]
```

### Required Parameters

`--model_deployment_id [str]`

The OCID of the Aqua MultiModel deployment.

`**kwargs`

Additional keyword arguments that can be used to filter the results for OCI get_model_deployment API. For more details on acceptable parameters, see [Get Model Deployment API](https://docs.oracle.com/iaas/api/#/en/data-science/20190101/ModelDeployment/GetModelDeployment).

### Example

```bash
ads aqua deployment get --model_deployment_id "ocid1.datasciencemodeldeployment.oc1.iad.<ocid>"
```

#### CLI Output

```json
{
    "id": "ocid1.datasciencemodeldeploymentint.oc1.iad.<ocid>",
    "display_name": "Multi model deployment of Mistral-7B-v0.1 and falcon-7b on A10.2",
    "aqua_service_model": false,
    "model_id": "ocid1.datasciencemodel.oc1.iad.<ocid>",
    "models": [
        {
            "model_id": "ocid1.datasciencemodel.oc1.iad.<ocid>",
            "model_name": "mistralai/Mistral-7B-v0.1",
            "gpu_count": 1,
            "env_var": {}
        },
        {
            "model_id": "ocid1.datasciencemodel.oc1.iad.<ocid>",
            "model_name": "tiiuae/falcon-7b",
            "gpu_count": 1,
            "env_var": {}
        }
    ],
    "aqua_model_name": "",
    "state": "ACTIVE",
    "description": null,
    "created_on": "2025-03-10 19:09:40.793000+00:00",
    "created_by": "ocid1.user.oc1..<ocid>",
     "endpoint": "https://modeldeployment.us-ashburn-1.oci.customer-oci.com/ocid1.datasciencemodeldeployment.oc1.iad.<ocid>",
    "private_endpoint_id": null,
    "console_link": "https://cloud.oracle.com/data-science/model-deployments/ocid1.datasciencemodeldeployment.oc1.iad.<ocid>",
    "lifecycle_details": "Model Deployment is Active.",
    "shape_info": {
        "instance_shape": "VM.GPU.A10.2",
        "instance_count": 1,
        "ocpus": null,
        "memory_in_gbs": null
    },
    "tags": {
        "aqua_model_id": "ocid1.datasciencemodel.oc1.iad.<ocid>",
        "aqua_multimodel": "true",
        "OCI_AQUA": "active"
    },
    "environment_variables": {
        "MODEL_DEPLOY_PREDICT_ENDPOINT": "/v1/chat/completions",
        "MULTI_MODEL_CONFIG": "{\"models\": [{\"params\": \"--served-model-name mistralai/Mistral-7B-v0.1 --seed 42 --tensor-parallel-size 1 --max-model-len 4096\", \"model_path\": \"service_models/Mistral-7B-v0.1/78814a9/artifact\"}, {\"params\": \"--served-model-name tiiuae/falcon-7b --seed 42 --tensor-parallel-size 1 --trust-remote-code\", \"model_path\": \"service_models/falcon-7b/f779652/artifact\"}]}",
        "MODEL_DEPLOY_ENABLE_STREAMING": "true",
        "PORT": "8080",
        "HEALTH_CHECK_PORT": "8080"
    },
    "cmd": [],
    "log_group": {
        "id": "ocid1.loggroup.oc1.iad.<ocid>",
        "name": "aqua-multimodel-deploy-log-group",
        "url": "https://cloud.oracle.com/logging/log-groups/ocid1.loggroup.oc1.iad.<ocid>?region=us-ashburn-1"
    },
    "log": {
        "id": "ocid1.log.oc1.iad.<ocid>",
        "name": "multi-model-create",
        "url": ""
    }
}
```

# MultiModel Inferencing

The only change required to infer a specific model from a MultiModel deployment is to update the value of `"model"` parameter in the request payload. The values for this parameter can be found in the Model Deployment details, under the field name `"model_name"`. This parameter segregates the request flow, ensuring that the inference request is directed to the correct model within the MultiModel deployment.

## Using oci-cli

```bash
oci raw-request --http-method POST --target-uri <model_deployment_url>/predict --request-body '{
        "model": "<model_name>",
        "prompt":"what are activation functions?",
        "max_tokens":250,
        "temperature": 0.7,
        "top_p":0.8,
    }' --auth <auth_method>
```

Note: Currently `oci-cli` does not support streaming response, use Python or Java SDK instead.


## Using Python SDK (without streaming)

```python
# The OCI SDK must be installed for this example to function properly.
# Installation instructions can be found here: https://docs.oracle.com/en-us/iaas/Content/API/SDKDocs/pythonsdk.htm

import requests
import oci
from oci.signer import Signer
from oci.config import from_file

config = from_file('~/.oci/config')
auth = Signer(
    tenancy=config['tenancy'],
    user=config['user'],
    fingerprint=config['fingerprint'],
    private_key_file_location=config['key_file'],
    pass_phrase=config['pass_phrase']
)

# For security token based authentication
# token_file = config['security_token_file']
# token = None
# with open(token_file, 'r') as f:
#     token = f.read()
# private_key = oci.signer.load_private_key_from_file(config['key_file'])
# auth = oci.auth.signers.SecurityTokenSigner(token, private_key)

model = "<model_name>"

endpoint = "https://modeldeployment.us-ashburn-1.oci.oc-test.com/ocid1.datasciencemodeldeployment.oc1.iad.xxxxxxxxx/predict"
body = {
    "model": model, # this is a constant
    "prompt": "what are activation functions?",
    "max_tokens": 250,
    "temperature": 0.7,
    "top_p": 0.8,
}

res = requests.post(endpoint, json=body, auth=auth, headers={}).json()

print(res)
```

## Using Python SDK (with streaming)

To consume streaming Server-sent Events (SSE), install [sseclient-py](https://pypi.org/project/sseclient-py/) using `pip install sseclient-py`.

```python
# The OCI SDK must be installed for this example to function properly.
# Installation instructions can be found here: https://docs.oracle.com/en-us/iaas/Content/API/SDKDocs/pythonsdk.htm

import requests
import oci
from oci.signer import Signer
from oci.config import from_file
import sseclient # pip install sseclient-py

config = from_file('~/.oci/config')
auth = Signer(
    tenancy=config['tenancy'],
    user=config['user'],
    fingerprint=config['fingerprint'],
    private_key_file_location=config['key_file'],
    pass_phrase=config['pass_phrase']
)

# For security token based authentication
# token_file = config['security_token_file']
# token = None
# with open(token_file, 'r') as f:
#     token = f.read()
# private_key = oci.signer.load_private_key_from_file(config['key_file'])
# auth = oci.auth.signers.SecurityTokenSigner(token, private_key)

model = "<model_name>"

endpoint = "https://modeldeployment.us-ashburn-1.oci.oc-test.com/ocid1.datasciencemodeldeployment.oc1.iad.xxxxxxxxx/predict"
body = {
    "model": model, # this is a constant
    "prompt": "what are activation functions?",
    "max_tokens": 250,
    "temperature": 0.7,
    "top_p": 0.8,
    "stream": True,
}

headers={'Content-Type':'application/json','enable-streaming':'true', 'Accept': 'text/event-stream'}
response = requests.post(endpoint, json=body, auth=auth, stream=True, headers=headers)

print(response.headers)

client = sseclient.SSEClient(response)
for event in client.events():
    print(event.data)

# Alternatively, we can use the below code to print the response.
# for line in response.iter_lines():
#    if line:
#        print(line)
```

## Using Python SDK for /v1/chat/completions endpoint

To access the model deployed with `/v1/chat/completions` endpoint for inference, update the body and replace `prompt` field
with `messages`.

```python
...
body = {
    "model": "<model_name>", # this is a constant
    "messages":[{"role":"user","content":[{"type":"text","text":"Who wrote the book Harry Potter?"}]}],
    "max_tokens": 250,
    "temperature": 0.7,
    "top_p": 0.8,
}
...
```

## Using Java (with streaming)

```java
/**
 * The OCI SDK must be installed for this example to function properly.
 * Installation instructions can be found here: https://docs.oracle.com/en-us/iaas/Content/API/SDKDocs/javasdk.htm
 */
package org.example;

import com.oracle.bmc.auth.AuthenticationDetailsProvider;
import com.oracle.bmc.auth.SessionTokenAuthenticationDetailsProvider;
import com.oracle.bmc.http.ClientConfigurator;
import com.oracle.bmc.http.Priorities;
import com.oracle.bmc.http.client.HttpClient;
import com.oracle.bmc.http.client.HttpClientBuilder;
import com.oracle.bmc.http.client.HttpRequest;
import com.oracle.bmc.http.client.HttpResponse;
import com.oracle.bmc.http.client.Method;
import com.oracle.bmc.http.client.jersey.JerseyHttpProvider;
import com.oracle.bmc.http.client.jersey.sse.SseSupport;
import com.oracle.bmc.http.internal.ParamEncoder;
import com.oracle.bmc.http.signing.RequestSigningFilter;

import javax.ws.rs.core.MediaType;
import java.io.BufferedReader;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.net.URI;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.function.Function;

public class RestExample {

    public static void main(String[] args) throws Exception {
        String configurationFilePath = "~/.oci/config";
        String profile = "DEFAULT";

        // Pre-Requirement: Allow setting of restricted headers. This is required to allow the SigningFilter
        // to set the host header that gets computed during signing of the request.
        System.setProperty("sun.net.http.allowRestrictedHeaders", "true");

        final AuthenticationDetailsProvider provider =
                new SessionTokenAuthenticationDetailsProvider(configurationFilePath, profile);

        // 1) Create a request signing filter instance using SessionTokenAuth Provider.
        RequestSigningFilter requestSigningFilter = RequestSigningFilter.fromAuthProvider(
                provider);

      //  1) Alternatively, RequestSigningFilter can be created from a config file.
      //  RequestSigningFilter requestSigningFilter = RequestSigningFilter.fromConfigFile(configurationFilePath, profile);

        // 2) Create a Jersey client and register the request signing filter.
        // Refer to this page https://docs.oracle.com/en-us/iaas/Content/API/SDKDocs/javasdkexamples.htm for information regarding the compatibility of the HTTP client(s) with OCI SDK version.

        HttpClientBuilder builder = JerseyHttpProvider.getInstance()
                .newBuilder()
                .registerRequestInterceptor(Priorities.AUTHENTICATION, requestSigningFilter)
                .baseUri(
                        URI.create(
                                "${modelDeployment.modelDeploymentUrl}/")
                                + ParamEncoder.encodePathParam("predict"));
        // 3) Create a request and set the expected type header.

        String jsonPayload = "{}";  // Add payload here with respect to your model example shown in next line:

        // 4) Setup Streaming request
        Function<InputStream, List<String>> generateTextResultReader = getInputStreamListFunction();
        SseSupport sseSupport = new SseSupport(generateTextResultReader);
        ClientConfigurator clientConfigurator = sseSupport.getClientConfigurator();
        clientConfigurator.customizeClient(builder);

        try (HttpClient client = builder.build()) {
            HttpRequest request = client
                    .createRequest(Method.POST)
                    .header("accepts", MediaType.APPLICATION_JSON)
                    .header("content-type", MediaType.APPLICATION_JSON)
                    .header("enable-streaming", "true")
                    .body(jsonPayload);

            // 5) Invoke the call and get the response.
            HttpResponse response = request.execute().toCompletableFuture().get();

            // 6) Print the response headers and body
            Map<String, List<String>> responseHeaders = response.headers();
            System.out.println("HTTP Headers " + responseHeaders);

            InputStream responseBody = response.streamBody().toCompletableFuture().get();
            try (
                    final BufferedReader reader = new BufferedReader(
                            new InputStreamReader(responseBody, StandardCharsets.UTF_8)
                    )
            ) {
                String line;
                while ((line = reader.readLine()) != null) {
                    System.out.println(line);
                }
            }
        } catch (Exception ex) {
            throw ex;
        }
    }

    private static Function<InputStream, List<String>> getInputStreamListFunction() {
        Function<InputStream, List<String>> generateTextResultReader = entityStream -> {
            try (BufferedReader reader =
                         new BufferedReader(new InputStreamReader(entityStream))) {
                String line;
                List<String> generatedTextList = new ArrayList<>();
                while ((line = reader.readLine()) != null) {
                    if (line.isEmpty() || line.startsWith(":")) {
                        continue;
                    }
                    generatedTextList.add(line);
                }
                return generatedTextList;
            } catch (Exception ex) {
                throw new RuntimeException(ex);
            }
        };
        return generateTextResultReader;
    }
}

```

## Multiple Inference endpoints

The support for multiple model deployment inference endpoints ensures flexibility and enables users to perform inferencing on any endpoint, regardless of the endpoint specified during deployment creation.

To access the supported endpoint by TGI/vLLM, you need to include `--request-headers '{"route":"<inference_endpoint>"}'` in the command and update the `--request-body`  according to the endpoint's contract.

```bash
oci raw-request --http-method POST --target-uri <model_deployment_url>/predict --request-headers '{"route":<inference_endpoint>}' --request-body  <request_body> --auth <auth_method>
```

```bash
## If "/v1/completions" was selected during deployment using vLLM SMC and "/v1/chat/completions" endpoint is required later on.

oci raw-request --http-method POST --target-uri  <model_deployment_url>/predict --request-headers '{"route":"/v1/chat/completions"}' --request-body '
      {
          "model": "<model_name>",
          "messages":[{"role":"user","content":[{"type":"text","text":"Who wrote the book Harry Potter?"}]}],
          "max_tokens": 500,
          "temperature": 0.7,
          "top_p": 0.8,
      }' --auth security_token

```


# MultiModel Evaluations

## Create Model Evaluations

### Description

Creates a new evaluation model using an existing Aqua MultiModel deployment. For Multi-Model deployment, evaluations must be created separately for each model using the same model deployment OCID.

### Usage

```bash
ads aqua evaluation create [OPTIONS]
```

### Required Parameters

`--evaluation_source_id [str]`

The evaluation source id. Must be MultiModel deployment OCID.

`--evaluation_name [str]`

The name for evaluation.

`--dataset_path [str]`

The dataset path for the evaluation. Must be an object storage path. <br>
Example: `oci://<bucket>@<namespace>/path/to/the/dataset.jsonl`

`--report_path [str]`

The report path for the evaluation. Must be an object storage path. <br>
Example: `oci://<bucket>@<namespace>/report/path/`

`--model_parameters [str]`

The parameters for the evaluation. The `"model"` is required evaluation param in case of MultiModel deployment. The value can be found in the Model Deployment details, under the field name `"model_name"`.  <br>
Example: `'{"model": "mistralai/Mistral-7B-v0.1", "max_tokens": 500, "temperature": 0.7, "top_p": 1.0, "top_k": 50}'`


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
ads aqua evaluation create  --evaluation_source_id "ocid1.datasciencemodeldeployment.oc1.iad.<ocid>" --evaluation_name "test_evaluation" --dataset_path "oci://<bucket>@<namespace>/path/to/the/dataset.jsonl" --report_path "oci://<bucket>@<namespace>/report/path/" --model_parameters '{"model":"<model_name>","max_tokens": 500, "temperature": 0.7, "top_p": 1.0, "top_k": 50}' --shape_name "VM.Standard.E4.Flex" --block_storage_size 50 --metrics '[{"name": "bertscore", "args": {}}, {"name": "rouge", "args": {}}]
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
        "aqua_service_model": "ocid1.datasciencemodel.oc1.iad.<ocid>#Mistral-7B-v0.1",
        "OCI_AQUA": ""
    }
}
```

For other operations related to **Evaluation**, such as listing evaluations and retrieving evaluation details, please refer to [AQUA CLI tips](cli-tips.md)

