# Deploy LLM Models using BYOC

This guide demonstrates how to deploy and perform inference using AI Quick Action registered models with Oracle Data Science Service Managed Containers (SMC) powered by vLLM. In this example, we will use a model downloaded from Hugging Face specifically, [openai/gpt-oss-120b](https://huggingface.co/openai/gpt-oss-120b) from OpenAI. 


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
log_id = "ocid1.log.oc1.xxx.xxxxx"

instance_shape = "BM.GPU.H100.8"

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


```shell
# Login to huggingface using env variable
huggingface-cli login --token <HUGGINGFACE_TOKEN>
```

[This](https://huggingface.co/docs/huggingface_hub/en/guides/cli#download-an-entire-repository) provides more information on using `huggingface-cli` to download an entire repository at a given revision. Models in the HuggingFace hub are stored in their own repository.


```shell
# Select the the model that you want to deploy.

huggingface-cli download openai/gpt-oss-120b --local-dir models/gpt-oss-120b
```

## Upload Model to OCI Object Storage


```shell
oci os object bulk-upload --src-dir $local_dir --prefix gpt-oss-120b/ -bn <bucket_name> -ns <bucket_namespace> --auth "resource_principal"
```

## Create Model by Reference using ADS



```python
from ads.model.datascience_model import DataScienceModel

artifact_path = f"oci://{bucket}@{namespace}/{model_prefix}"

model = (
    DataScienceModel()
    .with_compartment_id(compartment_id)
    .with_project_id(project_id)
    .with_display_name("gpt-oss-120b ")
    .with_artifact(artifact_path)
)

model.create(model_by_reference=True)
```

## Inference container

vLLM is an easy-to-use library for LLM inference and server.  You can get the container image from [DockerHub](https://hub.docker.com/r/vllm/vllm-openai/tags).

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

If your tenancy is federated with Oracle Identity Cloud Service, use the format <tenancy-namespace>/oracleidentitycloudservice/<username>. You can then push the container image to the OCI Registry

```shell
docker tag vllm/vllm-openai:gptoss -t <region>.ocir.io/<tenancy>/vllm-odsc/vllm-openai:gptoss
docker push <region>.ocir.io/<tenancy>/vllm-odsc/vllm-openai:gptoss


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
container_image = "<region>.ocir.io/<tenancy>/vllm-odsc/vllm-openai:gptoss"  # name given to vllm image pushed to oracle  container registry
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
}

cmd_var = [
    "--model",
    f"/opt/ds/model/deployed_model/{model_prefix}",
    "--tensor-parallel-size",
    "2",
    "--port",
    "8080",
    "--served-model-name",
    "openai/gpt-oss-120b",
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

prompt="What amateur radio bands are best to use when there are solar flares?"

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


**Short answer:**  
During a solar flare the **higher HF bands (≈10 MHz and up)** tend to work best, while the **lower HF bands (≤ 15 MHz, especially 80 m/160 m)** are usually “blacked‑out” by D‑layer absorption.  The most usable bands are generally **15 m, 12 m, 10 m and, for a short burst, 6 m** (and occasionally VHF/UHF if a sporadic‑E layer is present).

Below is a practical guide that explains why, how to recognise the conditions, and what you can actually do on the air.

---

## 1. What a solar flare does to the ionosphere

| Phenomenon | How it affects propagation | Time scale |
|------------|---------------------------|-----------|
| **X‑ray & extreme‑UV burst** (seconds to minutes) | Sudden increase of ionisation in the **D‑layer (≈60‑90 km)** → **enhanced absorption** of HF signals, especially below ~15 MHz. | Immediate, lasts a few minutes (the “Sudden Ionospheric Disturbance”, SID). |
| **UV/EUV hardening** (minutes) | Raises the **E‑layer MUF** (Maximum Usable Frequency) → higher‑frequency HF can travel farther. | 5–30 min after flare onset. |
| **Cosmic‑ray induced ionisation (in the F‑layer)** | Slightly improves F‑layer density → modest long‑term HF enhancement on the high bands. | Hours‑to‑days after a large flare. |
| **Associated CME & geomagnetic storm** (hours‑days) | If a coronal mass ejection follows, it can cause **geomagnetic disturbance** (Kp ↑) → spread‑F, auroral absorption, and HF degradation on the very high bands (often > 30 MHz). | Hours‑days later, a separate phenomenon from the prompt flare. |

> **Rule of thumb:**  
> *If you see a sudden loss of signal on 80 m/40 m/20 m right after a flare, the D‑layer is “turned on”. Switch to a band above the current MUF (typically 15 m‑10 m) and you’ll often get a clear opening.*

---

## 2. Which amateur bands survive – and why

| Band (approx.) | Typical behavior during a flare | Why it works (or fails) |
|----------------|--------------------------------|------------------------|
| **160 m (1.8 – 2.0 MHz)** | Almost always **dead** during the X‑ray burst. | Deep D‑layer absorption; low MUF. |
| **80 m (3.5 – 4.0 MHz)** | Heavy fade‑out; may recover only after the X‑ray flux drops. | Still within D‑layer absorption zone. |
| **60 m (5.3 – 5.4 MHz, US only)** | Similar to 80 m; may see short “pings” when the flare decays. | Near the edge of D‑layer absorption. |
| **40 m (7.0 – 7.3 MHz)** | Often dead for the first 5‑15 min; may recover later if the flare is modest (C‑class). | Still vulnerable; MUF may stay < 7 MHz. |
| **30 m (10.1 – 10.15 MHz)** | **Best of the lower HF**; can survive a weak flare but usually fades with M‑class or stronger events. | Near the D‑layer limit; occasional openings. |
| **20 m (14.0 – 14.35 MHz)** | **Usually usable**, especially on the rising edge of the flare when the MUF is driven up. | Above the D‑layer cut‑off, and the **MUF often rises to 18‑20 MHz**. |
| **17 m (18.068 – 18.168 MHz)** | Good, often better than 20 m during the flare peak. | MUF can exceed 20 MHz. |
| **15 m (21.0 – 21.45 MHz)** | **Very reliable** for a few minutes to an hour after the flare begins. | Well above the absorption region; the ionosphere is “pumped up”. |
| **12 m (24.89 – 24.99 MHz)** | Excellent when the flare is strong (M‑ or X‑class). | High MUF, low absorption. |
| **10 m (28.0 – 29.7 MHz)** | Often the **best** band during and immediately after a strong flare; can support worldwide contacts if the Sun is active. | MUF frequently > 30 MHz; propagation driven by the F‑layer. |
| **6 m (50‑54 MHz)** | **Sporadic‑E openings** can appear for 5‑30 min after a strong flare, giving VHF‑range contacts. | The flare can trigger short‑lived enhancements of the E‑layer irregularities. |
| **2 m/70 cm (144‑148 MHz, 430‑440 MHz)** | Mostly unaffected except during **auroral absorption** from a subsequent geomagnetic storm. | Propagation is line‑of‑sight; solar flare impact is minimal. |

**Bottom line:** **15 m, 12 m and 10 m are the “go‑to” bands** when a flare erupts. If you have a VHF setup, keep an eye on **6 m** for a brief Sporadic‑E window.

---

## 3. How to know a flare is occurring (real‑time tools)

| Tool | What it shows | How to use it for band choice |
|------|----------------|-------------------------------|
| **NOAA Space Weather Prediction Center (SWPC) – X‑ray flux plot** | GOES satellite X‑ray flux (C, M, X class) in 0.1‑8 Å band, updated every minute. | When **≥ M‑class** appears, expect D‑layer absorption. Move to > 10‑MHz bands. |
| **NOAA A‑index & K‑index** | Global geomagnetic activity. A‑index spikes during flare‑related ionospheric disturbances. | A‑index > 5 → D‑layer absorption heavy; stay on high HF. |
| **NASA DSCOVR + ACE real‑time solar wind data** | Solar wind speed, density, Bz. Useful for upcoming CME (hours later). | If a CME is inbound, plan for later geomagnetic storm; may need to drop back to lower bands after the flare fades. |
| **Ham‑radio specific sites** (e.g., *DXMaps*, *SolarHam*, *N4EP’s Solar Flare Alerts*) | Summarise current solar flux, sunspot number, and flare alerts. | Quick check before a night‑time contest or QSO. |
| **Propagation prediction software** (VOACAP, Ham Radio Deluxe, Hamlib *propagation* tools) | Calculates MUF and expected signal‑to‑noise for given time, band, and solar conditions. | Input current solar flux (S‑index) and A‑index to see which bands will be above the MUF. |

---

## 4. Practical operating tips

1. **Listen first.** Tune a 20 m or 15 m receiver while the flare is active. If you can hear stations that were silent before, the MUF has risen.
2. **Keep a “band‑switch” plan.** Have a preset list:  
   - **Start:** 20 m (if you’re already there).  
   - **If dead:** Jump to 15 m → 12 m → 10 m.  
   - **If you have a 6 m rig:** Try a quick “Sporadic‑E” sweep (73 – 75 MHz) after the flare’s peak.
3. **Power & antennas.** Higher frequencies need slightly more power for the same distance because free‑space loss rises with frequency, but the reduced absorption more than compensates. A simple half‑wave dipole on 10 m or a vertical with a good ground works well.
4. **Log the time.** Note the exact UTC time of the flare onset (you can copy the GOES timestamp). This data is useful for later propagation analysis and for other hams.
5. **Avoid the “N‑range” (near‑field) on VHF/UHF** during an accompanying geomagnetic storm, as auroral absorption can produce erratic signal fading.
6. **Be ready for rapid fade‑out.** Flares can cause a *Sudden Ionospheric Disturbance* that lasts only a few minutes. If you’re on a low band, you may get a brief “ripple” of S‑SB on SSB or CW before the signal disappears; switch to a higher band immediately.

---

## 5. Example scenario

| Time (UTC) | Solar event | Ionospheric effect | Recommended band(s) |
|------------|-------------|--------------------|----------------------|
| 12:30 | **C‑class flare** peaks (1 × 10⁻⁶ W/m²) | Mild D‑layer absorption; MUF rises to ~13 MHz. | 20 m still usable, 15 m opens. |
| 12:35 | **M‑class flare** peaks (5 × 10⁻⁵ W/m²) | Strong D‑layer absorption; MUF climbs to 18‑20 MHz. | Switch to 15 m, 12 m, 10 m. |
| 12:40 | **X‑class flare** peaks (1 × 10⁻⁴ W/m²) | D‑layer blackout of < 15 MHz; MUF may exceed 25 MHz for ~10 min. | 10 m is best; try 6 m if you have a VHF rig. |
| 12:55 | Flare decays, A‑index spikes to 7 | D‑layer recovers; MUF drops back to ~16‑18 MHz. | Return to 15 m/12 m; 20 m may become usable again after ~15 min. |

---

## 6. Quick “cheat sheet” for the radio operator

| Solar flare class | Expected absorption (low HF) | MUF trend | Best bands (immediate) |
|-------------------|------------------------------|-----------|------------------------|
| **C‑class** | Light | 10‑13 MHz | 20 m → 15 m |
| **M‑class** | Moderate → heavy | 15‑20 MHz | 15 m, 12 m, 10 m |
| **X‑class** | Very heavy (D‑layer blackout) | 20‑30 MHz+ (short‑lived) | 10 m, 12 m, 15 m, 6 m (if you have it) |

**Remember:**  
- The **higher the class**, the *more* the low bands are suppressed, **but the *higher* the MUF becomes**.  
- The **effect lasts only a few minutes** (the X‑ray burst); the **enhanced propagation on high HF may linger for 30‑60 min** as the ionosphere “settles”.

---

## 7. Resources you can bookmark

| Resource | URL | What you get |
|----------|-----|--------------|
| NOAA Space Weather Prediction Center (SWPC) – X‑ray flux | <https://www.swpc.noaa.gov/online-data/goes-x-ray-flux> | Real‑time flare intensities. |
| Space Weather Live – Solar Data | <https://www.spaceweatherlive.com/> | Solar flux (S‑index), sunspot number, flare alerts. |
| VOACAP Online (propagation predictions) | <https://qsl.net/kb9v/voacap/> | MUF, signal‑to‑noise for any band/time. |
| Ham Radio Deluxe “Propagation” window | (Desktop software) | Instant MUF for your location. |
| N4EP Solar Flare Alerts (email) | <https://n4ep.com/> | Short‑msg alerts for strong flares. |
| DXMaps – Current band conditions | <https://dxmaps.com/> | Crowd‑sourced band opening reports. |

---

### Bottom line

- **When a flare erupts, drop to the **higher HF** part of the spectrum (≥ 15 m, preferably 12 m‑10 m).**  
- **Avoid the lower HF bands** (80 m, 40 m, 30 m) while the X‑ray burst is on‑line.  
- **If you have a VHF kit, try 6 m** after the flare’s peak for a brief Sporadic‑E window.  
- **Monitor real‑time solar data** (GOES X‑ray, A‑index) and use a propagation tool (VOACAP) to confirm the current MUF before you switch.

Happy DX’ing, and may the Sun be with you!
