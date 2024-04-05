# Deploy TensorRT model in NVIDIA Triton Inference Server
This document provides a walkthrough for deploying Falcon TensorRT ensemble model with a NVIDIA [Triton Inference Server](https://developer.nvidia.com/nvidia-triton-inference-server) using OCI Data Science Model Deployment's bring your own container [(BYOC)](https://docs.oracle.com/en-us/iaas/data-science/using/mod-dep-byoc.htm) support.

The sample used here is based on [Triton's inflight_batcher_llm](https://github.com/triton-inference-server/tensorrtllm_backend/tree/47b609b670d6bb33a5ff113d98ad8a44d961c5c6/all_models/inflight_batcher_llm).

The Falcon Model TensorRT engine files need to be built using [TensorRT-LLM/examples/falcon](https://github.com/NVIDIA/TensorRT-LLM/tree/release/0.5.0/examples/falcon).

# Prerequisites

## Hardware Requirements

| GPU | Total GPU Memory    | Price per hour (For Pay-as-you-go, on-demand, Nov 2023)    |
| :-----: | :---: | :---: |
| VM.GPU.A10.1 (1x NVIDIA A10 Tensor Core) | 24GB   | $2   |
| VM.GPU.A10.2 (2x NVIDIA A10 Tensor Core) | 48GB (2x 24GB)   | $4 ($2 per node per hour)   |
| BM.GPU.A10.4 (4x NVIDIA A10 Tensor Core) | 96GB (4x 24GB)   | $8 ($2 per node per hour)   |
| BM.GPU4.8 (8x NVIDIA A100 40GB Tensor Core) | 320GB (8x 40GB)   | $24.4 ($3.05 per node per hour)   |
| BM.GPU.H100.8 (8x NVIDIA H100 80GB Tensor Core) | 640GB (8x 80GB)   | $80 ($10 per node per hour)   |

## Environment Setup 
Start by building a docker image which contain the tool chain required convert a huggingface hosted model into tensorRT-llm  compatible artifact, We can also use the same docker image for deploying the model for evaluation:

### Step 1 - Build the base image
```bash
  git clone https://github.com/triton-inference-server/tensorrtllm_backend.git
  cd tensorrtllm_backend/
  git submodule update --init —recursive
  DOCKER_BUILDKIT=1 docker build -t triton_trt_llm -f dockerfile/Dockerfile.trt_llm_backend .
```

### Step 2 - Downloading and Retrieving the model weights 
```bash
  git lfs install
  git clone https://huggingface.co/tiiuae/falcon-7b-instruct
```
### Step 3 - Compiling the Model 
The subsequent phase involves converting the model into a TensorRT engine. This requires having both the model weights and a model definition crafted using the TensorRT-LLM Python API. Within the TensorRT-LLM repository, there is an extensive selection of pre-established model structures. For the purpose of this blog, we'll employ the provided Falcon model definition rather than creating a custom one. This serves as a basic illustration of some optimizations that TensorRT-LLM offers. 
```bash
  # -v /falcon-7b/:/model:Z , This statement mounts the downloaded model directory into tooling container
  docker run --gpus=all --shm-size=1g -v /falcon-7b/:/model:Z -it triton_trt_llm bash
  # Inside the container , Run following command
  export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/cuda-12.2/compat/lib.real/
```

### Step 4 - Perform next 2 steps, only if Quantisation is required for your model
Install Quantisation tooling dependencies 

```bash
  # Run following commands in container prompt
  cuda_version=$(nvcc --version | grep 'release' | awk '{print $6}' | awk -F'[V.]' '{print $2$3}’)
  python_version=$(python3 --version 2>&1 | awk '{print $2}' | awk -F. '{print $1$2}’)
  
  # Download ammo framework required for Quantization
  wget https://developer.nvidia.com/downloads/assets/cuda/files/nvidia-ammo/nvidia_ammo-0.3.0.tar.gz
  tar -xzf nvidia_ammo-0.3.0.tar.gz
  pip install nvidia_ammo-0.3.0/nvidia_ammo-0.3.0+cu$cuda_version-cp$python_version-cp$python_version-linux_x86_64.whl
```

### Step 5 - Apply Quantisation and TensorRT-LLM conversion
```bash
  # Run following commands in container prompt
  cd tensorrt_llm/examples/falcon/
  
  # Install model specific dependencies
  pip install -r requirements.txt
  
  # Apply quantisation
  python quantize.py --model_dir /model \
                    --dtype float16 \
                    --qformat fp8 \
                    --export_path quantized_fp8 \
                    --calib_size 16
  
  # Apply TensorRT-LLM Conversion

  # Single GPU on falcon-7b-instruct
  python build.py --model_dir falcon/7b-instruct \
                  --dtype bfloat16 \
                  --use_gemm_plugin bfloat16 \
                  --remove_input_padding \
                  --use_gpt_attention_plugin bfloat16 \
                  --enable_context_fmha \
                  --output_dir falcon/7b/trt_engines/bf16/1-gpu/ \
                  --world_size 1
  # --output_dir falcon/7b/trt_engines/bf16/1-gpu/ indicates that converted model artifacts will be placed in this location.
````

# Model Deployment

Set up Triton Inference Server compliant docker image and model
### Step 1: Create Model Artifact
To use Triton, we need to build a model repository. The structure of the repository as follows:
```
falcon-7b-trt
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
        +-- falcon_float16_tp1_rank0.engine     (saved from TensorRT-LLM Conversion)
        +-- model.cache                         (saved from TensorRT-LLM Conversion)
        +-- config.json                         (saved from TensorRT-LLM Conversion)
        +-- falcon-7b                           (holds Original Model files)
```
Notes -

1. The attached falcon-7b-trt model doesn't have the falcon-7b trt converted model(`falcon_float16_tp1_rank0.engine`) in the repo. That needs to be created and put inside the model_artifact by the user with other files as shown above.
2. `falcon-7b` inside `tensorrt_llm/1` location is a folder which would have tokenizer and other files from the original model - [falcon-7b](https://huggingface.co/tiiuae/falcon-7b-instruct).
3. Model Deployment Service mounts the deployed_model at this location - `/opt/ds/model/deployed_model`. You can find the reference in the config.pbtxt, refer the `tokenizer_dir` [here](https://github.com/oracle-samples/oci-data-science-ai-samples/blob/main/model-deployment/containers/Triton_TensorRT/falcon-7b-trt/preprocessing/config.pbtxt)


### Step 2: Upload model artifact to Model catalog
Please zip the model_repository folder into model_artifact.zip and follow guidelines mentioned in [Readme step](https://github.com/oracle-samples/oci-data-science-ai-samples/blob/main/model-deployment/containers/llama2/README.md#one-time-download-to-oci-model-catalog) to create a model catalog item with model_artifact.zip.

### Step 3:  Upload NVIDIA base triton server image to OCI Container Registry

```bash
docker login $(OCIR_REGION).ocir.io
docker tag triton_trt_llm $(OCIR_REGION).ocir.io/$(OCIR_NAMESPACE)/oci-datascience-triton-server/triton-tensorrt:1.1
docker push $(OCIR_REGION).ocir.io/$(OCIR_NAMESPACE)/oci-datascience-triton-server/triton-tensorrt:1.1
```

### Step 4: Create Model Deployment
OCI Data Science Model Deployment has a dedicated support for Triton image, to make it easier to manage the Triton image by mapping of service-mandated endpoints to the Triton's inference and health HTTP/REST endpoint. 

To enable this support, enter the following environment variable when creating the Model Deployment:
```bash
CONTAINER_TYPE = TRITON
```
***
But Triton TRT Container serves the prediction on `/generate` endpoint instead of `/infer` which older Triton Container supports. OCI Data Science Model Deployment doesn't have a dedicated support for this new Triton TRT Image. 

So User can use Environment Variable supported by OCI Data Science Model Deployment service to serve this Triton TRT Container until OCI Data Science Model Deployment service provides dedicated support for the new Triton TRT image.
1. `MODEL_DEPLOY_PREDICT_ENDPOINT` Environment Variable to map the predict endpoint to `/v2/models/ensemble/versions/1/generate`. With this restriction, user can only inference single Model with TritonTRT MD as inference endpoint is a static endpoint.
2. `MODEL_DEPLOY_HEALTH_ENDPOINT` Environment Variable to map the health endpoint `/v2/health/ready`
3. This Triton TRT container constitutes around 40+ GB in Size, so OCI Model Deployment needs large enough Boot Volume to accommodate the same. For that purpose, user can use `STORAGE_SIZE_IN_GB` Environment Variable.

#### Using Python sdk
```bash
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
    environment_variables={
      'STORAGE_SIZE_IN_GB': '500', 
      'MODEL_DEPLOY_PREDICT_ENDPOINT':'/v2/models/ensemble/versions/1/generate', 
      'MODEL_DEPLOY_HEALTH_ENDPOINT':'/v2/health/ready'},
    image="iad.ocir.io/testtenancy/oci-datascience-triton-server/triton-tensorrt:1.1",
    image_digest=<image_digest>,
    cmd=[
        "tritonserver",
        "--model-repository=/opt/ds/model/deployed_model/falcon-7b-trt",
        "--http-port=9000"
    ],
    server_port=9000,
    health_check_port=9000
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

# Testing the model

## Using Python SDK to query the Inference Server

Specify the JSON inference payload with input and output layers for the model as well as describe the shape and datatype of the expected input and output:
```bash

import json

request_body = {"text_input": "Explain Cloud Computing to a school kid", "max_tokens": 30, "bad_words": ["now", "process"], "stop_words": [""], "top_k":20, "top_p":1, "end_id": 3, "pad_id": 2}
request_body = json.dumps(request_body)
```

No need to specify the request headers indicating model name and version as we need to do for older Triton Containers Inferencing. We have already mapped predict endpoint to static inference endpoint `/v2/models/ensemble/versions/1/generate` and the all the inference request to any Model would go to `ensemble` model only.
```bash
request_headers = {"model_name":"ensemble", "model_version":"1"}
```

Now, you can send an inference request to the Triton Inference Server:
```bash
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

## For testing via OCI CLI, after Model deployment becomes Green
```bash
  oci raw-request --http-method POST --target-uri https://<MODEL_DEPLOYMENT_URL>/predict --request-body '{"text_input": "What is the height of Eiffel Tower?", "max_tokens": 30, "bad_words": [""], "stop_words": [""], "top_k":10, "top_p":1, "end_id": 3, "pad_id": 2}'
```

## For testing locally on the host, start the triton server and make an http request
```bash
  # Run following commands in container prompt (Inside the tool chain container)
  tritonserver --model-repository <Location of model_repository folder having ensemble,preprocessor,postprocessor,tensorrt_llm>
  
  curl -X POST localhost:8000/v2/models/ensemble/versions/1/generate -d '{"text_input": "What is the height of Eiffel Tower?", "max_tokens": 30, "bad_words": [""], "stop_words": [""], "top_k":10, "top_p":1, "end_id": 3, "pad_id": 2}'
```