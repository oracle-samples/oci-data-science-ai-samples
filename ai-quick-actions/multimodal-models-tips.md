# Working with Multimodal Models

Currently we support all llama 3.2 family of vision models and `microsoft/Phi-3-vision-128k-instruct`. 

## Llama 3.2 Models

* Go to "Ready To Register" tab on AI Quick Actions and select the desired llama 3.2 model.
* Click on Regsiter button and follow the on screen instructions

## Phi-3-vision

* Proceed to Deploy section. There is no need to register

## Deploy

* Go to AI Quick Actions
* Click on Deployments
* Click on Create deployment
* Under model name select the desired vision model 
* (Optional) Select Shape
* (Optional) Select log group and log 
* (Required) Under `Inference mode`, select `v1/chat/completions` from the dropdown
* Click on Deploy

## Sample code 

The following python code demonstrates how to submit multi-modal inference payload.

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
