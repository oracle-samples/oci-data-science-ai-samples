# Deploy OpenAI open-source models

This guide demonstrates how to deploy and perform inference using OCI Data Science Service. In this example, we will use a model downloaded from Hugging Face, specifically [openai/gpt-oss-120b](https://huggingface.co/openai/gpt-oss-120b) from OpenAI. 

## Required IAM Policies

Add these [policies](https://github.com/oracle-samples/oci-data-science-ai-samples/tree/main/model-deployment/containers/llama2#required-iam-policies) to grant access to OCI services.

## Setup

Create a data science notebook session with at least 400GB of space. We will use a notebook session to: 
1. Download model weights
2. Create Model Catalog entry
3. Deploy the model

To prepare the inference container, we will use local laptop since this step requires Docker commands. The notebook session does not come with the docker tooling.


# Prepare Inference container

vLLM is an easy-to-use library for LLM inference and serving.  You can get the container image from [DockerHub](https://hub.docker.com/r/vllm/vllm-openai/tags).

Following commands are to run on your laptop - 

```shell
docker pull --platform linux/amd64 vllm/vllm-openai:gptoss
```

Currently, OCI Data Science Model Deployment only supports container images residing in the OCI Registry.  Before we can push the pulled vLLM container, make sure you have created a repository in your tenancy.  
- Go to your tenancy Container Registry
- Click on the Create repository button
- Select Private under Access types
- Set a name for Repository name.  We are using "vllm-odsc "in the example.
- Click on Create button

You may need to docker login to the Oracle Cloud Container Registry (OCIR) first, if you haven't done so before in order to push the image. To login, you have to use your API Auth Token that can be created under your Oracle Cloud Account->Auth Token. You need to login only once. Replace <region> with the OCI region you are using.

```shell
docker login -u '<tenant-namespace>/<username>' <region>.ocir.io
```

If your tenancy is federated with Oracle Identity Cloud Service, use the format <tenancy-namespace>/oracleidentitycloudservice/<username>. You can then push the container image to the OCI Registry:

```shell
docker tag vllm/vllm-openai:gptoss -t <region>.ocir.io/<tenancy>/vllm-odsc/vllm-openai:gptoss
docker push <region>.ocir.io/<tenancy>/vllm-odsc/vllm-openai:gptoss
```

# Deployment

Following steps are to be performed on OCI Notebook Session - 

## Prepare The Model Artifacts

To prepare Model artifacts for LLM model deployment:

- Download the model files from huggingface to local directory.
- Upload the model folder to a [versioned bucket](https://docs.oracle.com/en-us/iaas/Content/Object/Tasks/usingversioning.htm) in Oracle Object Storage. If you don’t have an Object Storage bucket, create one using the OCI SDK or the Console. Create an Object Storage bucket. Make a note of the `namespace`, `compartment`, and `bucketname`. Configure the policies to allow the Data Science service to read and write the model artifact to the Object Storage bucket in your tenancy. An administrator must configure the policies in IAM in the Console.
- Create model catalog entry for the model using the Object storage path

### Model Download from HuggingFace Model Hub

[This documentation](https://huggingface.co/docs/huggingface_hub/en/guides/cli#download-an-entire-repository) provides more information on using `huggingface-cli` to download an entire repository at a given revision. Models in the HuggingFace hub are stored in their own repository.


```shell
# Select the the model that you want to deploy.

huggingface-cli download openai/gpt-oss-120b --local-dir models/gpt-oss-120b --exclude metal/*
```

Download the titoken file - 

```shell
wget -P models/gpt-oss-120b https://openaipublic.blob.core.windows.net/encodings/o200k_base.tiktoken
```
## Upload Model to OCI Object Storage

**Note**: **The bucket has to be a versioned bucket**

```shell
oci os object bulk-upload --src-dir models/gpt-oss-120b --prefix gpt-oss-120b/ -bn <bucket_name> -ns <bucket_namespace> --auth "resource_principal"
```

## Create Model by Reference using ADS

```python
# Uncomment this code and set the correct proxy links if have to setup proxy for internet
# import os
# os.environ['http_proxy']="http://myproxy"
# os.environ['https_proxy']="http://myproxy"

# Use os.environ['no_proxy'] to route traffic directly
```


```python
import ads
import os

ads.set_auth("resource_principal")


# Extract region information from the Notebook environment variables and signer.
ads.common.utils.extract_region()
```

```python
# change as required for your environment
compartment_id = os.environ["PROJECT_COMPARTMENT_OCID"]
project_id = os.environ["PROJECT_OCID"]

log_group_id = "ocid1.loggroup.oc1.xxx.xxxxx"
log_id = "ocid1.log.oc1.xxx.xxxxx"

instance_shape = "BM.GPU.H100.8"

region = ads.common.utils.extract_region()
```

```python
from ads.model.datascience_model import DataScienceModel

bucket=<bucket-name>
namespace=<namespace>

artifact_path = f"oci://{bucket}@{namespace}/gpt-oss-120b"

model = (
    DataScienceModel()
    .with_compartment_id(compartment_id)
    .with_project_id(project_id)
    .with_display_name("gpt-oss-120b")
    .with_artifact(artifact_path)
)

model.create(model_by_reference=True)
```


### Import Model Deployment Modules

```python
from ads.model.deployment import (
    ModelDeployment,
    ModelDeploymentContainerRuntime,
    ModelDeploymentInfrastructure,
    ModelDeploymentMode,
)
```

## Setup Model Deployment Infrastructure

```python
container_image = "<region>.ocir.io/<tenancy>/vllm-odsc/vllm-openai:gptoss"  # name given to vllm image pushed to Oracle container registry
```

```python
infrastructure = (
    ModelDeploymentInfrastructure()
    .with_project_id(project_id)
    .with_compartment_id(compartment_id)
    .with_shape_name(instance_shape)
    .with_bandwidth_mbps(10)
    .with_replica(1)
    .with_web_concurrency(1)
    .with_access_log(
        log_group_id=log_group_id,
        log_id=log_id,
    )
    .with_predict_log(
        log_group_id=log_group_id,
        log_id=log_id,
    )
)
```

## Configure Model Deployment Runtime



```python
env_var = {
    "MODEL_DEPLOY_PREDICT_ENDPOINT": "/v1/chat/completions",
    "SHM_SIZE": "10g",
    "TIKTOKEN_RS_CACHE_DIR":"/opt/ds/model/gpt-oss-120b"    
}

cmd_var = [
    "--model",
    f"/opt/ds/model/deployed_model/gpt-oss-120b",
    "--tensor-parallel-size",
    "8",
    "--port",
    "8080",
    "--served-model-name",
    "openai/gpt-oss-120b",
    "--host",
    "0.0.0.0",
    "--trust-remote-code",
    "--quantization",
    "mxfp4"
]

container_runtime = (
    ModelDeploymentContainerRuntime()
    .with_image(container_image)
    .with_server_port(8080)
    .with_health_check_port(8080)
    .with_env(env_var)
    .with_cmd(cmd_var)
    .with_deployment_mode(ModelDeploymentMode.HTTPS)
    .with_model_uri(model.id)
    .with_region(region)
)
```

## Deploy Model using Container Runtime



```python
deployment = (
    ModelDeployment()
    .with_display_name(f"gpt-oss-120b MD with BYOC")
    .with_description(f"Deployment of gpt-oss-120b MD with vLLM BYOC container")
    .with_infrastructure(infrastructure)
    .with_runtime(container_runtime)
).deploy(wait_for_completion=False)
```


```python
deployment.watch()
```

## Inference


```python
import requests
from string import Template
from datetime import datetime


auth = ads.common.auth.default_signer()["signer"]
prompt = "What amateur radio bands are best to use when there are solar flares? Keep you response to 100 words"
endpoint = f"https://modeldeployment.us-ashburn-1.oci.customer-oci.com/{deployment.model_deployment_id}/predict"

current_date = datetime.now().strftime("%d %B %Y")

body = {
    "model": "openai/gpt-oss-120b",  # this is a constant
    "messages":[
        {"role": "user",
        "content": prompt
    }]
}
requests.post(endpoint, json=body, auth=auth, headers={}).json()
```

#### Output:


During solar flares the ionospheric D‑layer becomes heavily ionized, causing severe absorption of lower HF (3–10 MHz). The most reliable amateur bands are therefore the higher HF bands that are less affected—particularly 15 m (21 MHz), 12 m (24 MHz), 10 m (28 MHz) and the VHF/UHF “line‑of‑sight” bands (50 MHz, 70 MHz, 144 MHz, 432 MHz) which can still work via sporadic E or auroral propagation. If you must use lower HF, stick to the 20 m (14 MHz) band during the flare’s peak, as it often remains usable. Keep power modest and monitor real‑time solar flux indices.
