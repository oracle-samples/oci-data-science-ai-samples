# Deploy Meta Llama 3.1 8B

This how-to will show how to use the Oracle Data Science Service Managed Containers - to inference with a model downloaded from Hugging Face. For this we will use [Meta-Llama-3.1-8B-Instruct](https://huggingface.co/meta-llama/Meta-Llama-3.1-8B-Instruct) from Meta. The Llama 3 instruction tuned models are optimized for dialogue use cases and outperform many of the available open source chat models on common industry benchmarks. (with a custom commercial license, the Llama 3.1 Community License). With a context window of up to 128K and support across eight languages (English, German, French, Italian, Portuguese, Hindi, Spanish, and Thai), it rivals the top AI models when it comes to state-of-the-art capabilities in general knowledge, steerability, math, tool use, and multilingual translation.

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
container_image = "dsmc://odsc-vllm-serving:0.5.3.post1"   # official SMC image for vllm 0.5.3.post1
region = "us-ashburn-1"
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
HUGGINGFACE_TOKEN =  "<HUGGINGFACE_TOKEN>" # Your huggingface token
!huggingface-cli login --token $HUGGINGFACE_TOKEN
```

[This](https://huggingface.co/docs/huggingface_hub/guides/download#download-an-entire-repository) provides more information on using `snapshot_download()` to download an entire repository at a given revision. Models in the HuggingFace hub are stored in their own repository.

```python
# Download the LLama3.1 model from Hugging Face to a local folder.
#

from huggingface_hub import snapshot_download
from tqdm.auto import tqdm

model_name = "meta-llama/Meta-Llama-3.1-8B-Instruct" # copy from https://huggingface.co/meta-llama/Meta-Llama-3-8B-Instruct
local_dir = "models/Meta-Llama-3.1-8B-Instruct"

snapshot_download(repo_id=model_name, local_dir=local_dir, force_download=True, tqdm_class=tqdm)

print(f"Downloaded model {model_name} to {local_dir}")
```

## Upload Model to OCI Object Storage

```python
model_prefix = "Meta-Llama-3.1-8B-Instruct/" #"<bucket_prefix>"
bucket= "<bucket_name>" # this should be a versioned bucket
namespace = "<bucket_namespace>"

!oci os object bulk-upload --src-dir $local_dir --prefix $model_prefix -bn $bucket -ns $namespace --auth "resource_principal"
```

## Create Model by Reference using ADS

```python
from ads.model.datascience_model import DataScienceModel

artifact_path = f"oci://{bucket}@{namespace}/{model_prefix}"

model = (DataScienceModel()
  .with_compartment_id(compartment_id)
  .with_project_id(project_id)
  .with_display_name("Meta-Llama-3.1-8B-Instruct")
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

### Setup Model Deployment Infrastructure

```python
infrastructure = (
    ModelDeploymentInfrastructure()
    .with_project_id(project_id)
    .with_compartment_id(compartment_id)
    .with_shape_name(instance_shape)
    .with_bandwidth_mbps(10)
    .with_replica(1)
    .with_web_concurrency(10)
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

### Configure Model Deployment Runtime

```python
env_var = {
    'BASE_MODEL': model_prefix,
    'PARAMS': '--served-model-name llama3.1 --seed 42 --disable-custom-all-reduce',
    'MODEL_DEPLOY_PREDICT_ENDPOINT': '/v1/completions',
    'MODEL_DEPLOY_ENABLE_STREAMING': 'true',
}

container_runtime = (
    ModelDeploymentContainerRuntime()
    .with_image(container_image)
    .with_server_port(8080)
    .with_health_check_port(8080)
    .with_env(env_var)
    .with_deployment_mode(ModelDeploymentMode.HTTPS)
    .with_model_uri(model.id)
    .with_region(region)
)
```

### Deploy Model Using Container Runtime

```python
deployment = (
    ModelDeployment()
    .with_display_name(f"Meta-Llama-3.1-8B-Instruct with vLLM docker conatiner")
    .with_description("Deployment of Meta-Llama-3.1-8B-Instruct MD with vLLM(0.5.3.post1) container")
    .with_infrastructure(infrastructure)
    .with_runtime(container_runtime)
).deploy(wait_for_completion=False)
```

### Inference

Once the model deployment has reached the Active state, we can invoke the model deployment endpoint to interact with the LLM. More details on different ways for accessing MD endpoints is documented [here](https://github.com/oracle-samples/oci-data-science-ai-samples/blob/main/ai-quick-actions/model-deployment-tips.md).


#### How to prompt Llama 3.1

The base models have no prompt format. The Instruct versions use the following conversation structure:

```xml
<|begin_of_text|><|start_header_id|>system<|end_header_id|>

Cutting Knowledge Date: December 2023
Today Date: 29 Jul 2024

You are a helpful assistant<|eot_id|><|start_header_id|>user<|end_header_id|>

<prompt> <|eot_id|><|start_header_id|>assistant<|end_header_id|>
```

This format has to be exactly reproduced for effective use. More details about prompting LLaMA3.1 models can be found [here](https://llama.meta.com/docs/model-cards-and-prompt-formats/llama3_1).


```python
import requests
import ads
from string import Template
from datetime import datetime

ads.set_auth("resource_principal")
endpoint = f"https://modeldeployment.us-ashburn-1.oci.customer-oci.com/{deployment.model_deployment_id}/predict"

current_date = datetime.now().strftime("%d %B %Y")

prompt_template= Templatef(f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>

                    Cutting Knowledge Date: December 2023
                    Today Date: {current_date}

                    You are a helpful assistant<|eot_id|><|start_header_id|>user<|end_header_id|>

                    $prompt<|eot_id|><|start_header_id|>assistant<|end_header_id|>""")

prompt = prompt_template.substitute(prompt= "What amateur radio bands are best to use when there are solar flares?")

requests.post(
    endpoint,
    json={
        "model": "llama3.1",
        "prompt": prompt,
        "max_tokens": 500,
        "temperature": 0.7,
        "top_p": 0.8,
    },
    auth=ads.common.auth.default_signer()["signer"],
    headers={},
).json()

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
        "text": "\n\nDuring solar flares, it's best to use amateur radio bands that are less affected by the ionospheric and solar radiation. Here are some general guidelines:\n\n1. **Lower frequency bands (below 30 MHz):** These bands are less affected by solar activity and can be used for communication during solar flares. Some popular lower frequency bands include:\n\t* 160 meters (1.8-2 MHz)\n\t* 80 meters (3.5-4 MHz)\n\t* 40 meters (7-7.3 MHz)\n2. **Medium frequency bands (30-60 MHz):** These bands can be used, but with some caution. They may experience some ionospheric disturbances, but they can still be usable:\n\t* 20 meters (14-14.35 MHz)\n\t* 15 meters (21-21.45 MHz)\n\t* 10 meters (28-29.7 MHz)\n3. **Higher frequency bands (above 60 MHz):** These bands are more susceptible to ionospheric and solar radiation and are generally not recommended during solar flares:\n\t* 6 meters (50-54 MHz)\n\t* 2 meters (144-148 MHz)\n\t* 70 centimeters (430-440 MHz)\n\t* 23 centimeters (1240-1300 MHz)\n\nKeep in mind that the impact of solar flares on amateur radio bands can vary depending on the intensity of the flare and the specific frequency band. It's always a good idea to monitor the solar activity forecast and adjust your operating frequency accordingly.\n\nAdditionally, consider the following tips:\n\n* Use a solar flux index (SFI) and Kp index to monitor solar activity.\n* Be prepared for increased noise and interference on the higher frequency bands.\n* Use a good quality antenna and transmitter to minimize signal degradation.\n* Consider using a filter or a noise-reducing device to minimize interference.\n* Be patient and flexible, as propagation conditions can change rapidly during solar flares.\n\nRemember, it's always better to err on the side of caution and choose lower frequency bands during solar flares."
      }
    ],
    "created": 1722278476,
    "id": "cmpl-640c5f4febcb48798278506eadfd795e",
    "model": "odsc-llm",
    "object": "text_completion",
    "usage": {
      "completion_tokens": 431,
      "prompt_tokens": 58,
      "total_tokens": 489
    }
  },
```

During solar flares, it's best to use amateur radio bands that are less affected by the ionospheric and solar radiation. Here are some general guidelines:

1. **Lower frequency bands (below 30 MHz):** These bands are less affected by solar activity and can be used for communication during solar flares. Some popular lower frequency bands include:
	* 160 meters (1.8-2 MHz)
	* 80 meters (3.5-4 MHz)
	* 40 meters (7-7.3 MHz)
2. **Medium frequency bands (30-60 MHz):** These bands can be used, but with some caution. They may experience some ionospheric disturbances, but they can still be usable:
	* 20 meters (14-14.35 MHz)
	* 15 meters (21-21.45 MHz)
	* 10 meters (28-29.7 MHz)
3. **Higher frequency bands (above 60 MHz):** These bands are more susceptible to ionospheric and solar radiation and are generally not recommended during solar flares:
	* 6 meters (50-54 MHz)
	* 2 meters (144-148 MHz)
	* 70 centimeters (430-440 MHz)
	* 23 centimeters (1240-1300 MHz)

Keep in mind that the impact of solar flares on amateur radio bands can vary depending on the intensity of the flare and the specific frequency band. It's always a good idea to monitor the solar activity forecast and adjust your operating frequency accordingly.

Additionally, consider the following tips:

* Use a solar flux index (SFI) and Kp index to monitor solar activity.
* Be prepared for increased noise and interference on the higher frequency bands.
* Use a good quality antenna and transmitter to minimize signal degradation.
* Consider using a filter or a noise-reducing device to minimize interference.
* Be patient and flexible, as propagation conditions can change rapidly during solar flares.

Remember, it's always better to err on the side of caution and choose lower frequency bands during solar flares.


#### Using the model from [LangChain](https://python.langchain.com/v0.1/docs/integrations/llms/oci_model_deployment_endpoint/)

```python
import ads
from langchain_community.llms import OCIModelDeploymentVLLM
from string import Template
from datetime import datetime


ads.set_auth("resource_principal")
current_date = datetime.now().strftime("%d %B %Y")

llm = OCIModelDeploymentVLLM(
    endpoint=f"https://modeldeployment.us-ashburn-1.oci.customer-oci.com/{deployment.model_deployment_id}/predict",
    model="llama3.1",
)

llm.invoke(
    input=Template(f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>

                    Cutting Knowledge Date: December 2023
                    Today Date: {current_date}

                    You are a helpful assistant<|eot_id|><|start_header_id|>user<|end_header_id|>

                    $prompt<|eot_id|><|start_header_id|>assistant<|end_header_id|>""")
          .substitute(prompt="What amateur radio bands are best to use when there are solar flares?"),
    max_tokens=500,
    temperature=0.7,
    p=0.8,
    stop=["<|eot_id|>"],
    skip_special_tokens=False,
)
```
