# Working with Multimodal Models

Multimodal models accept inputs such as images or audio in addition to text. The following models are available in the supported AQUA model catalog. The linked publisher model cards describe their capabilities; the modalities and endpoints available in a deployment depend on its container and configuration.

## Supported multimodal models

| Model | Revision | Input modalities | Output | Usage |
| --- | --- | --- | --- | --- |
| [meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8](https://huggingface.co/meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8) | `ec4f1f9` | Text and images | Text | Instruction-based chat and image understanding. |
| [meta-llama/Llama-4-Scout-17B-16E-Instruct](https://huggingface.co/meta-llama/Llama-4-Scout-17B-16E-Instruct) | `c2b440b` | Text and images | Text | Instruction-based chat and image understanding. |
| [meta-llama/Llama-4-Scout-17B-16E](https://huggingface.co/meta-llama/Llama-4-Scout-17B-16E) | `14d516b` | Text and images | Text | Pretrained base model; do not assume instruction-tuned chat behavior. |
| [microsoft/Phi-3-vision-128k-instruct](https://huggingface.co/microsoft/Phi-3-vision-128k-instruct) | `fea3f11` | Text and images | Text | Image understanding, OCR, and chart/table questions; best suited to a single image per prompt. |
| [microsoft/Phi-3.5-vision-instruct](https://huggingface.co/microsoft/Phi-3.5-vision-instruct) | `4a0d683` | Text and images | Text | Image understanding, OCR, and multi-image comparison. |
| [microsoft/Phi-4-multimodal-instruct](https://huggingface.co/microsoft/Phi-4-multimodal-instruct) | `0af439b` | Text, images, and audio | Text | Image understanding and speech tasks; confirm the required adapters and endpoint configuration for each modality. |
| [ibm-granite/granite-vision-3.2-2b](https://huggingface.co/ibm-granite/granite-vision-3.2-2b) | `936cfb0` | Text and images | Text | Visual document understanding, including tables, charts, and diagrams. |
| [ibm-granite/granite-speech-3.3-8b](https://huggingface.co/ibm-granite/granite-speech-3.3-8b) | `df28cad` | Text and audio | Text | Speech recognition and speech translation; does not accept images. |

For affected service models and migration considerations, see [Deprecated Models and Replacement Options](deprecated-models.md).

Select the desired model in AQUA Model Explorer. If registration is required, follow the [model registration guide](register-tips.md); otherwise proceed to deployment. Confirm the supported shape, container, and inference mode for the selected model using the [model deployment guide](model-deployment-tips.md).

## Deploy

The following steps cover instruction-tuned vision models using an image-capable chat completions endpoint. For the Scout base model, use the supported prompt format and inference mode for that deployment. Audio input for Phi-4 and Granite Speech requires a compatible audio endpoint and payload; the image example below does not apply to audio requests.

* Go to AI Quick Actions
* Click on Deployments
* Click on Create deployment
* Under model name select the desired vision model 
* (Optional) Select Shape
* (Optional) Select log group and log 
* (Required) Under `Inference mode`, select `v1/chat/completions` from the dropdown
* Click on Deploy

## Sample code 

The following Python code demonstrates an image inference payload for `microsoft/Phi-3-vision-128k-instruct`. The `<|image_1|>` prompt token is model-specific; adapt the prompt format for other vision models.

```
import requests
import requests
from string import Template
import base64
import ads
 
endpoint="<Your Model Deployment Endpoint>"
image_path = "<Sample Image>"                                                        


# Set Resource principal. For other signers, please check `oracle-ads` documentation
ads.set_auth("resource_principal")

auth = ads.common.auth.default_signer()['signer']
 
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")
                                                           
                                                           
header = {"Content-Type": "application/json"}
payload = {
    "model": "odsc-llm",
    "messages": [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": Template("""<|image_1|>\n $prompt""").substitute(prompt="What is shown in this image?")},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{encode_image(image_path)}"
                    },
                },
            ],
        }
    ],
    "max_tokens": 500,
    "temperature": 0,
    "top_p": 0.9,
}
 
response=requests.post(endpoint, json=payload, auth=auth, headers={}).json()
print(response)
```
