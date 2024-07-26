# Deploy Meta Llama 3.1 405B

This how-to will show how to use the Oracle Data Science Service Managed Containers - to inference with a model downloaded from Hugging Face. For this we will use [Meta-Llama-3.1-405B-Instruct](https://huggingface.co/meta-llama/Meta-Llama-3.1-405B-Instruct) from Meta. The Llama 3.1 405B is a state-of-the-art open source model (with a custom commercial license, the Llama 3.1 Community License). With a context window of up to 128K and support across eight languages (English, German, French, Italian, Portuguese, Hindi, Spanish, and Thai), it rivals the top AI models when it comes to state-of-the-art capabilities in general knowledge, steerability, math, tool use, and multilingual translation.

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

instance_shape = "BM.GPU.H100.8"
container_image = "<region>.ocir.io/<tenancy>/vllm-odsc/vllm-openai:v0.5.3.post1"  # name given to vllm image pushed to oracle  container registry
region = "us-ashburn-1"
```

The container image referenced above is an  offical container published by vLLM team:

- CUDA 12.4.1
- cuDNN 9
- Torch 2.3.1
- Python 3.10
- vLLM v0.5.3.post1

## Prepare The Model Artifacts

To prepare Model artifacts for LLM model deployment:

- Download the model files from huggingface to local directory using a valid huggingface token (only needed for gated models). If you don't have Huggingface Token, refer [this](https://huggingface.co/docs/hub/en/security-tokens) to generate one.
- Upload the model folder to a [versioned bucket](https://docs.oracle.com/en-us/iaas/Content/Object/Tasks/usingversioning.htm) in Oracle Object Storage. If you don’t have an Object Storage bucket, create one using the OCI SDK or the Console. Create an Object Storage bucket. Make a note of the `namespace`, `compartment`, and `bucketname`. Configure the policies to allow the Data Science service to read and write the model artifact to the Object Storage bucket in your tenancy. An administrator must configure the policies in IAM in the Console.
- Create model catalog entry for the model using the Object storage path

<style>
/* Style the tab */
.tab {
  overflow: hidden;
  border-bottom: 1px solid #ccc;
}

/* Style the buttons inside the tab */
.tab button {
  background-color: inherit;
  float: left;
  border: none;
  outline: none;
  cursor: pointer;
  padding: 14px 16px;
  transition: 0.3s;
  font-size: 17px;
}

/* Change background color of buttons on hover */
.tab button:hover {
  background-color: #ddd;
}

/* Create an active/current tablink class */
.tab button.active {
  background-color: #ccc;
}

/* Style the tab content */
.tabcontent {
  display: none;
  padding: 6px 12px;
  border-top: none;
}
</style>


<div class="tab">
  <button class="tablinks" onclick="openTab(event, '#llama3_1_8B')">llama3_1_8B</button>
  <button class="tablinks" onclick="openTab(event, '#llama3_1_70B')">llama3_1_70B</button>
  <button class="tablinks" onclick="openTab(event, '#llama3_1_405B')">llama3_1_405B</button>
</div>

<div id="#llama3_1_8B" class="tabcontent">
  <h3>llama3.1 8B</h3>
  <p>
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

model_name = "meta-llama/Meta-Llama-3.1-405B-Instruct" # copy from https://huggingface.co/meta-llama/Meta-Llama-3.1-405B-Instruct
local_dir = "models/Meta-Llama-3.1-405B-Instruct"

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
  .with_display_name("Meta-Llama-3.1-405B-Instruct")
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
    'MODEL_DEPLOY_PREDICT_ENDPOINT': '/v1/completions',
    'MODEL_DEPLOY_ENABLE_STREAMING': 'true',
    'SHM_SIZE': '10g'
}

cmd_var = ["--model", "/opt/ds/model/deployed_model/Meta-Llama-3-8B-Instruct/", "--tensor-parallel-size", "8", "--port", "8080", "--served-model-name", "llama3.1", "--host", "0.0.0.0", "--max-model-len", "1200", "--trust-remote-code"]

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

### Deploy Model Using Container Runtime

```python
deployment = (
    ModelDeployment()
    .with_display_name(f"Meta-Llama-3.1-405B-Instruct with vLLM docker conatiner")
    .with_description("Deployment of Meta-Llama-3.1-405B-Instruct MD with vLLM(0.5.3.post1) container")
    .with_infrastructure(infrastructure)
    .with_runtime(container_runtime)
).deploy(wait_for_completion=False)
```
  </p>
</div>
<div id="#llama3_1_70B" class="tabcontent">
  <h3>llama3.1 70B</h3>
  <p>
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

model_name = "meta-llama/Meta-Llama-3.1-405B-Instruct" # copy from https://huggingface.co/meta-llama/Meta-Llama-3.1-405B-Instruct
local_dir = "models/Meta-Llama-3.1-405B-Instruct"

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
  .with_display_name("Meta-Llama-3.1-405B-Instruct")
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
    'MODEL_DEPLOY_PREDICT_ENDPOINT': '/v1/completions',
    'MODEL_DEPLOY_ENABLE_STREAMING': 'true',
    'SHM_SIZE': '10g'
}

cmd_var = ["--model", "/opt/ds/model/deployed_model/Meta-Llama-3-8B-Instruct/", "--tensor-parallel-size", "8", "--port", "8080", "--served-model-name", "llama3.1", "--host", "0.0.0.0", "--max-model-len", "1200", "--trust-remote-code"]

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

### Deploy Model Using Container Runtime

```python
deployment = (
    ModelDeployment()
    .with_display_name(f"Meta-Llama-3.1-405B-Instruct with vLLM docker conatiner")
    .with_description("Deployment of Meta-Llama-3.1-405B-Instruct MD with vLLM(0.5.3.post1) container")
    .with_infrastructure(infrastructure)
    .with_runtime(container_runtime)
).deploy(wait_for_completion=False)
```
  </p>
</div>

</div>
<div id="#llama3_1_405B" class="tabcontent">
  <h3>llama3.1 405B</h3>
  <p>
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

model_name = "meta-llama/Meta-Llama-3.1-405B-Instruct" # copy from https://huggingface.co/meta-llama/Meta-Llama-3.1-405B-Instruct
local_dir = "models/Meta-Llama-3.1-405B-Instruct"

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
  .with_display_name("Meta-Llama-3.1-405B-Instruct")
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
    'MODEL_DEPLOY_PREDICT_ENDPOINT': '/v1/completions',
    'MODEL_DEPLOY_ENABLE_STREAMING': 'true',
    'SHM_SIZE': '10g'
}

cmd_var = ["--model", "/opt/ds/model/deployed_model/Meta-Llama-3-8B-Instruct/", "--tensor-parallel-size", "8", "--port", "8080", "--served-model-name", "llama3.1", "--host", "0.0.0.0", "--max-model-len", "1200", "--trust-remote-code"]

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

### Deploy Model Using Container Runtime

```python
deployment = (
    ModelDeployment()
    .with_display_name(f"Meta-Llama-3.1-405B-Instruct with vLLM docker conatiner")
    .with_description("Deployment of Meta-Llama-3.1-405B-Instruct MD with vLLM(0.5.3.post1) container")
    .with_infrastructure(infrastructure)
    .with_runtime(container_runtime)
).deploy(wait_for_completion=False)
```
  </p>
</div>

<script>
function openTab(evt, tabName) {
  var i, tabcontent, tablinks;
  tabcontent = document.getElementsByClassName("tabcontent");
  for (i = 0; i < tabcontent.length; i++) {
    tabcontent[i].style.display = "none";
  }
  tablinks = document.getElementsByClassName("tablinks");
  for (i = 0; i < tablinks.length; i++) {
    tablinks[i].className = tablinks[i].className.replace(" active", "");
  }
  document.getElementById(tabName).style.display = "block";
  evt.currentTarget.className += " active";
}
</script>

### Inference

Once the model deployment has reached the Active state, we can invoke the model deployment endpoint to interact with the LLM. More details on different ways for accessing MD endpoints is documented [here](https://github.com/oracle-samples/oci-data-science-ai-samples/blob/main/ai-quick-actions/model-deployment-tips.md).


#### How to prompt Llama 3.1

The base models have no prompt format. The Instruct versions use the following conversation structure:

```xml
<|begin_of_text|><|start_header_id|>system<|end_header_id|>

Cutting Knowledge Date: December 2023
Today Date: 25 Jul 2024

You are a helpful assistant<|eot_id|><|start_header_id|>user<|end_header_id|>

<prompt> <|eot_id|><|start_header_id|>assistant<|end_header_id|>
```

This format has to be exactly reproduced for effective use.


```python
import requests
import ads
from string import Template

ads.set_auth("resource_principal")

prompt_template= Template("""<|begin_of_text|><|start_header_id|>system<|end_header_id|>

                    Cutting Knowledge Date: December 2023
                    Today Date: 24 Jul 2024

                    You are a helpful assistant<|eot_id|><|start_header_id|>user<|end_header_id|>

                    $prompt<|eot_id|><|start_header_id|>assistant<|end_header_id|>""")

prompt = t.substitute(prompt= "What amateur radio bands are best to use when there are solar flares?")

requests.post(
    "https://modeldeployment.us-ashburn-1.oci.customer-oci.com/{deployment.model_deployment_id}/predict",
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
import ads
from langchain_community.llms import OCIModelDeploymentVLLM
from string import Template

ads.set_auth("resource_principal")

llm = OCIModelDeploymentVLLM(
    endpoint="https://modeldeployment.us-ashburn-1.oci.customer-oci.com/{deployment.model_deployment_id}/predict",
    model="llama3.1",
)

llm.invoke(
    input=Template("""<|begin_of_text|><|start_header_id|>system<|end_header_id|>

                    Cutting Knowledge Date: December 2023
                    Today Date: 24 Jul 2024

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
