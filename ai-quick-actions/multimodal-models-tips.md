# Working with Multimodal Models

## Deploy

* Go to AI Quick Actions
* Click on Deployments
* Click on Create deployment
* Under model name select `microsoft/Phi-3-vision-128k-instruct`
* Deployed `Phi3-vision-128k-Instruct` model using AI Quick Actions
* (Optional) Select Shape
* (Optional) Select log group and log 
* Click on `Show advanced options`
* (Required) Under Inference Model, select `v1/chat/completions` from the dropdown
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
                {"type": "text", "text": Template("""<|image_1|>\n""").substitute(prompt="What is shown in this image?")},
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