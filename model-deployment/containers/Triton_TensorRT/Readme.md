# Deploy TensorRT model in NVIDIA Triton Inference Server
This document provides a walkthrough for deploying Falcon TensorRT ensemble model into a NVIDIA [Triton Inference Server](https://developer.nvidia.com/nvidia-triton-inference-server) using OCI Data Science Modle Deployment's custom containers support.

The sample used here is based on [Triton's inflight_batcher_llm](https://github.com/triton-inference-server/tensorrtllm_backend/tree/47b609b670d6bb33a5ff113d98ad8a44d961c5c6/all_models/inflight_batcher_llm).

The Falcon Model TensorRT engine files need to be built using [TensorRT-LLM/examples/falcon](https://github.com/NVIDIA/TensorRT-LLM/tree/release/0.5.0/examples/falcon).

## Step 1: Set up Triton Inference Server
### Step 1.1: Create Model Artifact
To use Triton, we need to build a model repository. The structure of the repository as follows:
```
model_repository
|
+-- ensemble
    |
    +-- config.pbtxt
    +-- 1
+-- postprocessing
    |
    +-- config.pbtxt
    +-- 1
        |
        +-- model.py
+-- preprocessing
    |
    +-- config.pbtxt
    +-- 1
        |
        +-- model.py
+-- tensorrt_llm
    |
    +-- config.pbtxt
    +-- 1
        |
        +-- model.py
```


### Step 1.2  Upload NVIDIA base triton server image to OCI Container Registry

```
docker login $(OCIR_REGION).ocir.io
mkdir -p tritonServer
cd tritonServer
git clone https://github.com/triton-inference-server/server.git -b v2.30.0 --depth 1
cd server
python compose.py --backend onnxruntime --repoagent checksum --output-name $(OCIR_REGION).ocir.io/$(OCIR_NAMESPACE)/oci-datascience-triton-server/onnx-runtime:1.0.0
docker push $(OCIR_REGION).ocir.io/$(OCIR_NAMESPACE)/oci-datascience-triton-server/onnx-runtime:1.0.0
```

### Step 1.3 Upload model artifact to Model catalog
Compress model_repository folder created in Step 1.1 in zip format and upload it to model catalog. Refer to https://docs.oracle.com/en-us/iaas/data-science/using/models_saving_catalog.htm for details


### Step 1.4 Create Model Deployment
OCI Data Science Model Deployment has a dedicated support for Triton image, to make it easier to manage the Triton image by mapping of service-mandated endpoints to the Triton's inference and health HTTP/REST endpoint. To enable this support, enter the following environment variable when creating the Model Deployment:
```
CONTAINER_TYPE = TRITON
```

#### Using python sdk
```
# Create a model configuration details object
model_config_details = ModelConfigurationDetails(
    model_id= <model_id>,
    bandwidth_mbps = <bandwidth_mbps>,
    instance_configuration = <instance_configuration>,
    scaling_policy = <scaling_policy>
)
  
# Create the container environment configuration
environment_config_details = OcirModelDeploymentEnvironmentConfigurationDetails(
    environment_configuration_type="OCIR_CONTAINER",
    environment_variables={'CONTAINER_TYPE': 'TRITON'},
    image="iad.ocir.io/testtenancy/oci-datascience-triton-server/triton-tensorrt:1.1",
    image_digest=<image_digest>,
    cmd=[
        "tritonserver",
        "--model-repository=/opt/ds/model/deployed_model/model_repository"
    ],
    server_port=8000,
    health_check_port=8000
)
  
# create a model type deployment
single_model_deployment_config_details = data_science.models.SingleModelDeploymentConfigurationDetails(
    deployment_type="SINGLE_MODEL",
    model_configuration_details=model_config_details,
    environment_configuration_details=environment_config_details
)
  
# set up parameters required to create a new model deployment.
create_model_deployment_details = CreateModelDeploymentDetails(
    display_name= <deployment_name>,
    model_deployment_configuration_details = single_model_deployment_config_details,
    compartment_id = <compartment_id>,
    project_id = <project_id>
)
```

## Step 2: Using Python SDK to query the Inference Server

Specify the JSON inference payload with input and output layers for the model as well as describe the shape and datatype of the expected input and output:
```

import json

request_body = {"text_input": "Explain Cloud Computing to a school kid", "max_tokens": 30, "bad_words": ["now", "process"], "stop_words": [""], "top_k":20, "top_p":1, "end_id": 3, "pad_id": 2}
request_body = json.dumps(request_body)
```

Specify the request headers indicating model name and version:
```
request_headers = {"model_name":"ensemble", "model_version":"1"}
```

Now, you can send an inference request to the Triton Inference Server:
```
# The OCI SDK must be installed for this example to function properly.
# Installation instructions can be found here: https://docs.oracle.com/en-us/iaas/Content/API/SDKDocs/pythonsdk.htm
 
import requests
import oci
from oci.signer import Signer
 
config = oci.config.from_file("~/.oci/config") # replace with the location of your oci config file
auth = Signer(
  tenancy=config['tenancy'],
  user=config['user'],
  fingerprint=config['fingerprint'],
  private_key_file_location=config['key_file'],
  pass_phrase=config['pass_phrase'])
 
endpoint = <modelDeploymentEndpoint>
 
inference_output = requests.request('POST',endpoint, data=request_body, auth=auth, headers=request_headers).json()['outputs'][0]['data'][:5]
```