# LLM Stacked Inferencing

Ideal for scenarios involving large language models, this capability allows multiple fine-tuned weights to be packaged and deployed together with the base
model. The selected fine-tuned weights are applied at run time thereby maximising GPU utilisation and inference efficiency. This capability also aids in
performing A/B experimentation for a collection of fine-tuned weights.

To deploy this configuration, the model group feature is used create a logical grouping of the base and fine-tuned models and subsequently the model
group is deployed as a stacked inference model deployment.

The deployment type is as below

**STACKED**: This group is specifically designed for large language models (LLMs) with a base model and multiple fine-tuned weights.

> **Note**  
> Stacked Inferencing currently supports only **vLLM containers**.  
> To know more about features used during stacked inferencing, refer to the vLLM official user guide:https://docs.vllm.ai/en/stable/features/lora.html#dynamically-serving-lora-adapters.

## Deployment Steps

### 1. Create a Stacked Model Group

Use the model group feature to logically group the base and fine-tuned models.

### 2. Deployment Configuration

Update the deployment configuration with the stacked model group ID. Include the following in the `environmentVariables` for vLLM container:

```json
{
  "PARAMS": "--served-model-name <base_model_ocid> --max-model-len 2048 --enable_lora",
  "VLLM_ALLOW_RUNTIME_LORA_UPDATING": "True"
}
```

> 📌 These environment variables are subject to change with vLLM versions.

**LoRA Enablement:**  
The `--enable-lora` flag is necessary for vLLM to recognize LoRA adapters.  
See [vLLM Docs on LoRA](https://docs.vllm.ai/en/stable/features/lora.html#dynamically-serving-lora-adapters).

---

## Example Stacked Deployment Payload

```python
# Example Payload for stacked deployment
compartment_id = "compartmentID"
project_id = "projectID"
model_group_id = "StackedModelGroupId"

payload = {
    "displayName": "MMS Model Group Deployment - Stacked",
    "description": "mms",
    "compartmentId": compartment_id,
    "projectId": project_id,
    "modelDeploymentConfigurationDetails": {
        "deploymentType": "MODEL_GROUP",
        "modelGroupConfigurationDetails": {
            "modelGroupId": model_group_id
        },
        "infrastructureConfigurationDetails": {
            "infrastructureType": "INSTANCE_POOL",
            "instanceConfiguration": {
                "instanceShapeName": "VM.GPU.A10.1"
            },
            "scalingPolicy": {
                "policyType": "FIXED_SIZE",
                "instanceCount": 1
            }
        },
        "environmentConfigurationDetails": {
            "environmentConfigurationType": "OCIR_CONTAINER",
            "serverPort": 8080,
            "image": "iad.ocir.io/ociodscdev/dsmc/inferencing/odsc-vllm-serving:0.6.4.post1.1",
            "environmentVariables": {
                "MODEL_DEPLOY_PREDICT_ENDPOINT": "/v1/completions",
                "PARAMS": "--served-model-name <base_model_ocid> --max-lora-rank 64 --max-model-len 4096 --enable_lora",
                "PORT": "8080",
                "VLLM_ALLOW_RUNTIME_LORA_UPDATING": "true",
                "TENSOR_PARALLELISM": "1"
            }
        }
    },
    "categoryLogDetails": {
        "access": {
            "logGroupId": "<log_group_id>",
            "logId": "<log_id>"
        },
        "predict": {
            "logGroupId": "<log_group_id>",
            "logId": "<log_id>"
        }
    }
}
```

---

## Predict Call

> 📌 For using inference key, please pass the inference key value in the "model" key in lieu of the model_id in the below example.

```python
def predict(model_id_or_inference_key):
    predict_url = f'{endpoint}/{md_ocid}/predict'
    predict_data = json.dumps({
        "model": model_id_or_inference_key,
        "prompt": "[user] Write a SQL query to answer the question based on the table schema.\\n\\n context: CREATE TABLE table_name_74 (icao VARCHAR, airport VARCHAR)\\n\\n question: Name the ICAO for lilongwe international airport [/user] [assistant]",
        "max_tokens": 100,
        "temperature": 0
    })
    predict_headers = {
        'Content-Type': 'application/json',
        'opc-request-id': 'test-id'
    }

    response = requests.request("POST", predict_url, headers=predict_headers, data=predict_data, auth=auth, verify=False)
    util.print_response(response)

if __name__ == "__main__":

    baseModel = f"{base_model_ocid}"
    print("BaseModel", baseModel)
    predict(baseModel)

    lora1 = f'{ft_model_ocid2}
    print("FT-Weight1", lora1)
    predict(lora1)


    lora2 = f'{ft_model_ocid2}
    print("FT-Weight2", lora2)
    predict(lora2)
```

---

## Updating Fine-Tuned Weights

- Create a new **stacked model group** using either the `CREATE` or `CLONE` operation.
- Once the stacked model group is created, you can **add or remove fine-tuned weight models** from the group.


### Sample Create Payload with Updated Weights:

```python
compartment_id = "compartmentID"
project_id = "projectID"
mg_create_url = f"{endpoint}/modelGroups?compartmentId={compartment_id}"

mg_payload = json.dumps({
    "createType": "CREATE",
    "compartmentId": compartment_id,
    "projectId": project_id,
    "displayName": "Model Group - Stacked ",
    "description": "Test stacked model group",
    "modelGroupDetails": {
        "type": "STACKED",
        "baseModelId": f'{base_model_ocid}'
    },
    "memberModelEntries": {
        "memberModelDetails": [
            {
                "inferenceKey": "basemodel",
                "modelId": f'{base_model_ocid}'
            },
            {
                "inferenceKey": "sql-lora-2",
                "modelId": f'{updated_model_ocid_1}'
            },
            {
                "inferenceKey": "sql-lora-3",
                "modelId": f'{updated_model_ocid_2}'
            }
        ]
    }
})
```

---

## Live Update
Perform an update of the model deployment with the updated stacked model group id.

```python
compartment_id = "compartmentID"
project_id = "projectID"
md_ocid = f'{md_ocid}'
endpoint = 'https://modeldeployment-int.us-ashburn-1.oci.oc-test.com'

update_url = f"{endpoint}/modelDeployments/{mdocid}"
model_group_id_update = "update_modelGroupId"
update_payload = json.dumps({
    "displayName": "MMS Model Group Deployment - Stacked",
    "description": "mms",
    "compartmentId": compartment_id,
    "projectId": project_id,
    "modelDeploymentConfigurationDetails": {
        "deploymentType": "MODEL_GROUP",
        "updateType": "LIVE",
        "modelGroupConfigurationDetails": {
            "modelGroupId": model_group_id_update
        }
    }
})
response = requests.request("PUT", update_url, headers=util.headers, data=update_payload, auth=auth)
```

---

## Perform /predict call on the model deployment
> 📌 For using inference key, please pass the inference key value in the "model" key in lieu of the model_id in the below example.

```python
md_ocid = f'{md_ocid}
int_endpoint = 'https://modeldeployment-int.us-ashburn-1.oci.oc-test.com'
endpoint = int_endpoint
  
def predict(model_id):
  
    predict_url = f'{endpoint}/{md_ocid}/predict'
    predict_data = json.dumps({
        "model": model_id / inference_key,
        "prompt": "[user] Write a SQL query to answer the question based on the table schema.\\n\\n context: CREATE TABLE table_name_74 (icao VARCHAR, airport VARCHAR)\\n\\n question: Name the ICAO for lilongwe international airport [/user] [assistant]",
        "max_tokens": 100,
        "temperature": 0
    })
    predict_headers = {
        'Content-Type': 'application/json',
        'opc-request-id': 'test-id'
    }
  
    response = requests.request("POST", predict_url, headers=predict_headers, data=predict_data, auth=auth, verify=False)
    util.print_response(response)
  
  
if __name__ == "__main__":
      
    baseModel = f'{base_model_ocid}
    print("BaseModel", baseModel)
    predict(baseModel)
  
    lora1 = f'{lora_weight_1}
    print("lora-1", lora1)
    predict(lora1)
  
    lora2 = f'{lora_weight_2}
    print("lora-2", lora2)
    predict(lora2)
      
    lora3 = f'{lora_weight_3}
    print("lora-3", lora3)
    predict(lora3)
```

---

## References

- [vLLM Docs](https://docs.vllm.ai/en/stable/features/lora.html)
- [OCI Docs](https://docs.oracle.com/en-us/iaas/Content/data-science/using/model_dep_create.htm)