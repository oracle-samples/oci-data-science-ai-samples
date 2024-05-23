# Deploy Meta-Llama-3-8B-Instruct with Oracle Service Managed vLLM(0.3.0) Container

![LLama3](https://huggingface.co/blog/assets/llama3/thumbnail.jpg)

This how-to will show how to use the Oracle Data Science Service Managed Containers - part of the Quick Actions feature, to inference with a model downloaded from Hugging Face. For this we will use [Meta-Llama-3-8B-Instruct](https://huggingface.co/meta-llama/Meta-Llama-3-8B-Instruct) from Meta. The Llama 3 instruction tuned models are optimized for dialogue use cases and outperform many of the available open source chat models on common industry benchmarks.

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

instance_shape = "VM.GPU.A10.1"
container_image = "dsmc://odsc-vllm-serving:0.3.0.7"
region = "us-ashburn-1"
```

The container image referenced above (`dsmc://odsc-vllm-serving:0.3.0.7`) is an Oracle Service Managed container that was build with:

- Oracle Linux 8 - Slim
- CUDA 12.4
- cuDNN 9
- Torch 2.1.2
- Python 3.11.5
- vLLM v0.3.0

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
# Download the LLama3 model from Hugging Face to a local folder.
#

from huggingface_hub import snapshot_download
from tqdm.auto import tqdm

model_name = "meta-llama/Meta-Llama-3-8B-Instruct" # copy from https://huggingface.co/meta-llama/Meta-Llama-3-8B-Instruct
local_dir = "models/Meta-Llama-3-8B-Instruct"

snapshot_download(repo_id=model_name, local_dir=local_dir, force_download=True, tqdm_class=tqdm)  

print(f"Downloaded model {model_name} to {local_dir}")
```

## Upload Model to OCI Object Storage

```python
model_prefix = "Meta-Llama-3-8B-Instruct/" #"<bucket_prefix>" 
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
  .with_display_name("Meta-Llama-3-8B-Instruct")
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
    'PARAMS': '--served-model-name odsc-llm --seed 42', 
    'MODEL_DEPLOY_PREDICT_ENDPOINT': '/v1/completions', 
    'MODEL_DEPLOY_ENABLE_STREAMING': 'true'
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
    .with_display_name(f"Meta-Llama-3-8B-Instruct with vLLM SMC")
    .with_description("Deployment of Meta-Llama-3-8B-Instruct MD with vLLM(0.3.0) container")
    .with_infrastructure(infrastructure)
    .with_runtime(container_runtime)
).deploy(wait_for_completion=False)
```

### Inference

Once the model deployment has reached the Active state, we can invoke the model deployment endpoint to interact with the LLM. More details on different ways for accessing MD endpoints is documented [here](https://github.com/oracle-samples/oci-data-science-ai-samples/blob/main/ai-quick-actions/model-deployment-tips.md).


#### How to prompt Llama 3

The base models have no prompt format. The Instruct versions use the following conversation structure:

```xml
<|begin_of_text|><|start_header_id|>system<|end_header_id|>

{{ system_prompt }}<|eot_id|><|start_header_id|>user<|end_header_id|>

{{ user_msg_1 }}<|eot_id|><|start_header_id|>assistant<|end_header_id|>

{{ model_answer_1 }}<|eot_id|>
```

This format has to be exactly reproduced for effective use.


```python
import requests
import ads
from string import Template

ads.set_auth("resource_principal")

requests.post(
    "https://modeldeployment.us-ashburn-1.oci.customer-oci.com/{deployment.model_deployment_id}/predict",
    json={
        "model": "odsc-llm",
        "prompt": Template(
            """"|begin_of_text|><|start_header_id|>user<|end_header_id|> $prompt <|eot_id|><|start_header_id|>assistant<|end_header_id|>"""
        ).substitute(
            prompt="What amateur radio band can a general class license holder use?"
        ),
        "max_tokens": 250,
        "temperature": 0.7,
        "top_p": 0.8,
    },
    auth=ads.common.auth.default_signer()["signer"],
    headers={},
).json()
```

#### Output

The LLM produced a great output:

> A) All amateur radio bands
B) All amateur radio bands except the 10-meter band
C) All amateur radio bands except the 160-meter band
D) All amateur radio bands except the 2200-meter band
>
Answer: A) All amateur radio bands
\</s\>
>
The FCC grants a general class license to amateur radio operators who pass the Element 3 exam. The exam covers the following topics:
>
* FCC rules and regulations
* Amateur radio practices and procedures
* Radio theory and operating practices
* Antennas and transmission lines
* Electronic circuits and devices
* RF safety and environmental concerns
>
As a general class license holder, an amateur radio operator is authorized to use all amateur radio bands, which include:
>
* 160 meters (1.8 MHz to 2 MHz)
* 80 meters (3.5 MHz to 4 MHz)
* 40 meters (7 MHz to 7.3 MHz)
* 30 meters (10.1 MHz to 10.3 MHz)
* 20 meters (14 MHz to 14.3 MHz)
* 17 meters (18.1 MHz to 18.3 MHz)
* 15 meters (21 MHz to 21.3 MHz

The raw output:

```json
{
  "id": "cmpl-2d57a83cb6544b768abc00c1b3b7ffc5",
  "object": "text_completion",
  "created": 2277,
  "model": "odsc-llm",
  "choices": [
    {
      "index": 0,
      "text": "A) All amateur radio bands\nB) All amateur radio bands except the 10-meter band\nC) All amateur radio bands except the 160-meter band\nD) All amateur radio bands except the 2200-meter band\n\nAnswer: A) All amateur radio bands\n</s>\n\nThe FCC grants a general class license to amateur radio operators who pass the Element 3 exam. The exam covers the following topics:\n\n* FCC rules and regulations\n* Amateur radio practices and procedures\n* Radio theory and operating practices\n* Antennas and transmission lines\n* Electronic circuits and devices\n* RF safety and environmental concerns\n\nAs a general class license holder, an amateur radio operator is authorized to use all amateur radio bands, which include:\n\n* 160 meters (1.8 MHz to 2 MHz)\n* 80 meters (3.5 MHz to 4 MHz)\n* 40 meters (7 MHz to 7.3 MHz)\n* 30 meters (10.1 MHz to 10.3 MHz)\n* 20 meters (14 MHz to 14.3 MHz)\n* 17 meters (18.1 MHz to 18.3 MHz)\n* 15 meters (21 MHz to 21.3 MHz",
      "logprobs": null,
      "finish_reason": "length"
    }
  ],
  "usage": {
    "prompt_tokens": 19,
    "total_tokens": 269,
    "completion_tokens": 250
  }
}
```

#### Using the model from [LangChain](https://python.langchain.com/v0.1/docs/integrations/llms/oci_model_deployment_endpoint/)

```python
import ads
from langchain_community.llms import OCIModelDeploymentVLLM
from string import Template

ads.set_auth("resource_principal")

llm = OCIModelDeploymentVLLM(
    endpoint="https://modeldeployment.us-ashburn-1.oci.customer-oci.com/{deployment.model_deployment_id}/predict",
    model="odsc-llm",
)

llm.invoke(
    input=Template(
        """"|begin_of_text|><|start_header_id|>user<|end_header_id|> $prompt <|eot_id|><|start_header_id|>assistant<|end_header_id|>"""
    ).substitute(
        prompt="What amateur radio bands are best to use when there are solar flares?"
    ),
    max_tokens=500,
    temperature=0,
    p=0.9,
    stop=["<|eot_id|>"],
    skip_special_tokens=False,
)
```

Output:

> During solar flares, the ionosphere can become highly ionized, causing radio signals to be refracted and scattered in unpredictable ways. This can make it challenging to communicate on certain amateur radio bands. However, some bands are more affected than others. Here's a general guideline on which amateur radio bands to use during solar flares:
>
**Avoid:**
>
1. **HF (3-30 MHz) bands**: These bands are most affected by solar flares, as the ionosphere can become highly ionized, causing signal refraction and scattering. Signals may be severely attenuated or even completely absorbed.
2. **20m (14 MHz) and 15m (21 MHz) bands**: These bands are also prone to significant signal degradation due to the ionosphere's increased ionization.
>
**Use:**
>
1. **VHF (50-250 MHz) bands**: These bands are less affected by solar flares, as the ionosphere's ionization has less impact on signal propagation. Signals are more likely to follow a more predictable path.
2. **UHF (300-3000 MHz) bands**: These bands are even less affected by solar flares, as the ionosphere's ionization has a minimal impact on signal propagation.
3. **SHF (3-30 GHz) bands**: These bands are generally not affected by solar flares, as the ionosphere's ionization has a negligible impact on signal propagation.
>
**Tips:**
>
1. **Monitor propagation conditions**: Keep an eye on propagation forecasts and reports from other amateur radio operators to adjust your operating frequency and mode accordingly.
2. **Use digital modes**: Digital modes like PSK31, FT8, and JT65 are more resistant to signal degradation and can be a good choice during solar flares.
3. **Experiment with different frequencies**: If you're experiencing difficulties on a particular frequency, try switching to a different frequency within the same band to see if the signal improves.
4. **Keep an eye on the solar flare's impact**: Monitor the solar flare's intensity and duration to adjust your operating strategy accordingly.
>
Remember, solar flares can have unpredictable effects on radio propagation, so it's essential to stay flexible and adapt to changing conditions.