# Deploy ELYZA-japanese-Llama-2-13b-instruct with Oracle Service Managed vLLM(0.3.0) Container

![ELYZA](https://huggingface.co/elyza/ELYZA-japanese-Llama-2-13b/resolve/main/key_visual.png)

This how-to will show how to use the Oracle Data Science Service Managed Containers - part of the Quick Actions feature, to inference with a model downloaded from Hugging Face. For this we will use [ELYZA-japanese-Llama-2-13b-instruct](https://huggingface.co/collections/elyza/elyza-japanese-llama-2-13b-6589ba0435f23c0f1c41d32a) from a company named ELYZA, which is known for its LLM research and is based out of the University of Tokyo. ELYZA uses pre-training from the English-dominant model because of the prevalence of English training data, along with an additional 18 billion tokens of Japanese data.

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
# Download the ELYZA model from Hugging Face to a local folder.
#

from huggingface_hub import snapshot_download
from tqdm.auto import tqdm

model_name = "elyza/ELYZA-japanese-Llama-2-13b-instruct"
local_dir = "models/ELYZA-japanese-Llama-2-13b-instruct"

snapshot_download(repo_id=model_name, local_dir=local_dir, force_download=True, tqdm_class=tqdm)  

print(f"Downloaded model {model_name} to {local_dir}")
```

## Upload Model to OCI Object Storage

```python
model_prefix = "ELYZA-japanese-Llama-2-13b-instruct/" #"<bucket_prefix>" 
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
  .with_display_name("ELYZA-japanese-Llama-2-13b-instruct")
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
    .with_overwrite_existing_artifact(True)
    .with_remove_existing_artifact(True)
)
```

### Deploy Model Using Container Runtime

```python
deployment = (
    ModelDeployment()
    .with_display_name(f"ELYZA-japanese-Llama-2-13b-Instruct MD with vLLM SMC")
    .with_description("Deployment of ELYZA-japanese-Llama-2-13b-Instruct MD with vLLM(0.3.0) container")
    .with_infrastructure(infrastructure)
    .with_runtime(container_runtime)
).deploy(wait_for_completion=False)
```

### Inference

Once the model deployment has reached the Active state, we can invoke the model deployment endpoint to interact with the LLM. More details on different ways for accessing MD endpoints is documented [here](https://github.com/oracle-samples/oci-data-science-ai-samples/blob/main/ai-quick-actions/model-deployment-tips.md).

```python
import requests
import ads

ads.set_auth("resource_principal")

requests.post(
    "https://modeldeployment.us-ashburn-1.oci.customer-oci.com/{deployment.model_deployment_id}/predict",
    json={
        "model": "odsc-llm",  # do not change this with system managed container deployments
        "prompt": "{bos_token}{b_inst} {system} {prompt} {e_inst}".format(
            bos_token="<s>",
            b_inst="[INST]",
            system="<<SYS>>\nあなたは誠実で優秀な日本人のアシスタントです。\n<</SYS>>\n\n",
            prompt="活性化関数とは何ですか",
            e_inst="[/INST]",
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

The LLM produced a great output from the prompt *"what is an activation function?"*, which translates to:

>
> An activation function is a function that initializes the output of a neuron in a neural network that is part of a machine learning algorithm. 
> If the output of the neuron is x and the activation function is f, the new output y of the neuron can be calculated using the following formula. 
>
> y = f(x)
>
>Generally, neuron activation functions often have the following characteristics.
>
> 1. Monotonicity: In general, the relationship between input and output of an activation function is monotonic.
> 2. Differentiability: The activation function cannot be differentiated.
>


```python
{
    "id": "cmpl-807794826bf3438397e5e0552c0dcba8",
    "object": "text_completion",
    "created": 7343,
    "model": "odsc-llm",
    "choices": [
        {
            "index": 0,
            "text": "活性化関数とは、機械学習アルゴリズムの一部であるニューラルネットワークにおいて、ニューロンの出力を初期化するための関数のことです。\n\nニューロンの出力をxとし、活性化関数をfとすると、ニューロンの新たな出力yは以下の式で求められます。\n\ny = f(x)\n\n一般に、ニューロンの活性化関数は以下のような特性を持つものが多く使われています。\n\n1. 単調性: 活性化関数は、入力と出力の関係が単調であることが一般的です。\n2. 可微分性: 活性化関数は、微分が定義でき",
            "logprobs": None,
            "finish_reason": "length",
        }
    ],
    "usage": {"prompt_tokens": 86, "total_tokens": 336, "completion_tokens": 250},
}
```
