# Deploy LLM Models using BYOC

This guide demonstrates how to deploy and perform inference using AI Quick Action registered models with Oracle Data Science Service Managed Containers (SMC) powered by vLLM. In this example, we will use a model downloaded from Hugging Face specifically, [Meta-Llama-3.1-8B-Instruct](https://huggingface.co/meta-llama/Meta-Llama-3.1-8B-Instruct) from Meta. 


## Required IAM Policies

Add these [policies](https://github.com/oracle-samples/oci-data-science-ai-samples/tree/main/model-deployment/containers/llama2#required-iam-policies) to grant access to OCI services.

## Setup



```python
# Install required python packages

!pip install oracle-ads
!pip install oci
!pip install huggingface_hub
```


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
```


```python
# Extract region information from the Notebook environment variables and signer.
ads.common.utils.extract_region()
```

### Common variables


```python
# change as required for your environment
compartment_id = os.environ["PROJECT_COMPARTMENT_OCID"]
project_id = os.environ["PROJECT_OCID"]

log_group_id = "ocid1.loggroup.oc1.xxx.xxxxx"
log_id = "cid1.log.oc1.xxx.xxxxx"

instance_shape = "VM.GPU.A10.2"

region = "<your-region>"
```

## API Endpoint Usage

The `/v1/completions` is for interacting with non-chat base models or the instruction trained chat model. This endpoint provides the completion for a single prompt and takes a single string as input, whereas the `/v1/chat/completions` endpoint provides the responses for a given dialog and requires the input in a specific format corresponding to the message history. This guide uses `/v1/chat/completions` endpoint.


## Prepare The Model Artifacts

To prepare Model artifacts for LLM model deployment:

- Download the model files from huggingface to local directory using a valid huggingface token (only needed for gated models). If you don't have Huggingface Token, refer [this](https://huggingface.co/docs/hub/en/security-tokens) to generate one.
- Upload the model folder to a [versioned bucket](https://docs.oracle.com/en-us/iaas/Content/Object/Tasks/usingversioning.htm) in Oracle Object Storage. If you don’t have an Object Storage bucket, create one using the OCI SDK or the Console. Create an Object Storage bucket. Make a note of the `namespace`, `compartment`, and `bucketname`. Configure the policies to allow the Data Science service to read and write the model artifact to the Object Storage bucket in your tenancy. An administrator must configure the policies in IAM in the Console.
- Create model catalog entry for the model using the Object storage path

### Model Download from HuggingFace Model Hub


```python
# Login to huggingface using env variable
HUGGINGFACE_TOKEN = "<HUGGINGFACE_TOKEN>"  # Your huggingface token
!huggingface-cli login --token $HUGGINGFACE_TOKEN
```

[This](https://huggingface.co/docs/huggingface_hub/en/guides/cli#download-an-entire-repository) provides more information on using `huggingface-cli` to download an entire repository at a given revision. Models in the HuggingFace hub are stored in their own repository.


```python
# Select the the model that you want to deploy. Currently it is set to Meta-Llama3.1-8B-Instruct
model_name = "meta-llama/Meta-Llama-3.1-8B-Instruct"
local_dir = "models/Meta-Llama-3.1-8B-Instruct"

!huggingface-cli download $model_namet --local-dir $local_dir
```

## Upload Model to OCI Object Storage


```python
model_prefix = "Meta-Llama-3.1-8B-Instruct/"  # "<bucket_prefix>"
bucket = "<bucket_name>"  # this should be a versioned bucket
namespace = "<bucket_namespace>"

!oci os object bulk-upload --src-dir $local_dir --prefix $model_prefix -bn $bucket -ns $namespace --auth "resource_principal"
```

## Create Model by Reference using ADS



```python
from ads.model.datascience_model import DataScienceModel

artifact_path = f"oci://{bucket}@{namespace}/{model_prefix}"

model = (
    DataScienceModel()
    .with_compartment_id(compartment_id)
    .with_project_id(project_id)
    .with_display_name("Meta-Llama-3.1-405B-Instruct-FP8")
    .with_artifact(artifact_path)
)

model.create(model_by_reference=True)
```

## Inference container

vLLM is an easy-to-use library for LLM inference and server.  You can get the container image from [DockerHub](https://hub.docker.com/r/vllm/vllm-openai/tags).

```python
docker pull --platform linux/amd64 vllm/vllm-openai:latest
```

Currently, OCI Data Science Model Deployment only supports container images residing in the OCI Registry.  Before we can push the pulled vLLM container, make sure you have created a repository in your tenancy.  
- Go to your tenancy Container Registry
- Click on the Create repository button
- Select Private under Access types
- Set a name for Repository name.  We are using "vllm-odsc "in the example.
- Click on Create button

You may need to docker login to the Oracle Cloud Container Registry (OCIR) first, if you haven't done so before in order to push the image. To login, you have to use your API Auth Token that can be created under your Oracle Cloud Account->Auth Token. You need to login only once. Replace <region> with the OCI region you are using.

```python
docker login -u '<tenant-namespace>/<username>' <region>.ocir.io
```

If your tenancy is federated with Oracle Identity Cloud Service, use the format <tenancy-namespace>/oracleidentitycloudservice/<username>. You can then push the container image to the OCI Registry

```python
docker tag vllm/vllm-openai:v0.5.3.post1 -t <region>.ocir.io/<tenancy>/vllm-odsc/vllm-openai:latest
docker push <region>.ocir.io/<tenancy>/vllm-odsc/vllm-openai:latest


```python
container_image = "<region>.ocir.io/<tenancy>/vllm-odsc/vllm-openai:latest"  # name given to vllm image pushed to oracle  container registry
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
    "MODEL_DEPLOY_PREDICT_ENDPOINT": "/v1/completions",
}

cmd_var = [
    "--model",
    f"/opt/ds/model/deployed_model/{model_prefix}",
    "--tensor-parallel-size",
    "2",
    "--port",
    "8080",
    "--served-model-name",
    "odsc-llm",
    "--host",
    "0.0.0.0",
    "--trust-remote-code",
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
    .with_display_name(f"{model_prefix} MD with BYOC")
    .with_description(f"Deployment of {model_prefix} MD with vLLM BYOC container")
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
prompt = "What amateur radio bands are best to use when there are solar flares?"
endpoint = f"https://modeldeployment.us-ashburn-1.oci.customer-oci.com/{deployment.model_deployment_id}/predict"

current_date = datetime.now().strftime("%d %B %Y")
prompt_template = Template(
    """"<|begin_of_text|><|start_header_id|>system<|end_header_id|>

                    Cutting Knowledge Date: December 2023
                    Today Date: {current_date}

                    You are a helpful assistant<|eot_id|><|start_header_id|>user<|end_header_id|>

                    $prompt<|eot_id|><|start_header_id|>assistant<|end_header_id|>"""
)

prompt = t.substitute(
    prompt="What amateur radio bands are best to use when there are solar flares?"
)

body = {
    "model": "odsc-llm",  # this is a constant
    "prompt": prompt,
    "max_tokens": 500,
    "temperature": 0,
    "top_p": 0.9,
}
requests.post(endpoint, json=body, auth=auth, headers={}).json()
```

#### Output:

The raw output:

```json
{
  "data": {
    "choices": [
      {
        "finish_reason": "stop",
        "index": 0,
        "logprobs": null,
        "stop_reason": null,
        "text": "\n\nDuring solar flares, radio communications can be disrupted due to increased ionization and geomagnetic storms. However, some amateur radio bands are more resilient to these conditions than others. Here are some bands that are often considered best to use during solar flares:\n\n1. **VHF (30 MHz - 300 MHz) and UHF (300 MHz - 3 GHz) bands**: These higher frequency bands are less affected by solar flares and geomagnetic storms. They are also less prone to ionospheric absorption, which can attenuate signals on lower frequency bands.\n2. **6 meters (50 MHz)**: This band is often considered a good choice during solar flares, as it is less affected by ionospheric disturbances and can provide reliable local and regional communications.\n3. **2 meters (144 MHz) and 70 cm (440 MHz)**: These bands are popular for local and regional communications and are often less affected by solar flares.\n4. **Microwave bands (e.g., 1.2 GHz, 2.4 GHz, 5.8 GHz)**: These bands are even less affected by solar flares and can provide reliable communications over shorter distances.\n\nBands to avoid during solar flares:\n\n1. **HF (3 MHz - 30 MHz) bands**: These lower frequency bands are more susceptible to ionospheric absorption and geomagnetic storms, which can cause signal loss and disruption.\n2. **160 meters (1.8 MHz) and 80 meters (3.5 MHz)**: These bands are often the most affected by solar flares and geomagnetic storms.\n\nKeep in mind that the impact of solar flares on amateur radio communications can vary depending on the intensity of the flare, the location of the communicating stations, and the time of day. It's always a good idea to monitor space weather forecasts and adjust your communication plans accordingly."
      }
    ],
    "created": 1721939892,
    "id": "cmpl-4aac6ee35ffd477eaedadbb973efde18",
    "model": "llama3.1",
    "object": "text_completion",
    "usage": {
      "completion_tokens": 384,
      "prompt_tokens": 57,
      "total_tokens": 441
    }
  },
```

During solar flares, radio communications can be disrupted due to increased ionization and geomagnetic storms. However, some amateur radio bands are more resilient to these conditions than others. Here are some bands that are often considered best to use during solar flares:

1. **VHF (30 MHz - 300 MHz) and UHF (300 MHz - 3 GHz) bands**: These higher frequency bands are less affected by solar flares and geomagnetic storms. They are also less prone to ionospheric absorption, which can attenuate signals on lower frequency bands.
2. **6 meters (50 MHz)**: This band is often considered a good choice during solar flares, as it is less affected by ionospheric disturbances and can provide reliable local and regional communications.
3. **2 meters (144 MHz) and 70 cm (440 MHz)**: These bands are popular for local and regional communications and are often less affected by solar flares.
4. **Microwave bands (e.g., 1.2 GHz, 2.4 GHz, 5.8 GHz)**: These bands are even less affected by solar flares and can provide reliable communications over shorter distances.

Bands to avoid during solar flares:

1. **HF (3 MHz - 30 MHz) bands**: These lower frequency bands are more susceptible to ionospheric absorption and geomagnetic storms, which can cause signal loss and disruption.
2. **160 meters (1.8 MHz) and 80 meters (3.5 MHz)**: These bands are often the most affected by solar flares and geomagnetic storms.

Keep in mind that the impact of solar flares on amateur radio communications can vary depending on the intensity of the flare, the location of the communicating stations, and the time of day. It's always a good idea to monitor space weather forecasts and adjust your communication plans accordingly.


#### Using the model from [LangChain](https://python.langchain.com/v0.1/docs/integrations/llms/oci_model_deployment_endpoint/)


```python
from langchain_community.llms import OCIModelDeploymentVLLM
from string import Template
from datetime import datetime

ads.set_auth("resource_principal")
current_date = datetime.now().strftime("%d %B %Y")

llm = OCIModelDeploymentVLLM(
    endpoint=f"https://modeldeployment.us-ashburn-1.oci.customer-oci.com/{deployment.model_deployment_id}/predict",
    model="odsc-llm",
)

llm.invoke(
    input=Template(
        f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>

                    Cutting Knowledge Date: December 2023
                    Today Date:{current_date}

                    You are a helpful assistant<|eot_id|><|start_header_id|>user<|end_header_id|>

                    $prompt<|eot_id|><|start_header_id|>assistant<|end_header_id|>"""
    ).substitute(
        prompt="What amateur radio bands are best to use when there are solar flares?"
    ),
    max_tokens=500,
    temperature=0.7,
    p=0.8,
    stop=["<|eot_id|>"],
    skip_special_tokens=False,
)
```
