# Guide to update models following TGI Deprecation

## List of model's container upgraded from TGI to VLLM
1. **codegemma-1.1-2b**
2. **codegemma-1.1-7b-it**
3. **codegemma-2b**
4. **codegemma-7b**
5. **falcon-40b-instruct**
6. **gemma-1.1-7b-it**
7. **gemma-2b**
8. **gemma-2b-it**
9. **gemma-7b**

## Impact
Any model deployment associated with the above models will fail on restart.

## Mitigation 1 - Update the existing registered model 
If you have registered one of the above models, update the model configuration to use **VLLM** container in place of **TGI** during deployment. To update the registered model and create new deployment on **VLLM** follow the below instructions.

1. Use the **Get Model** Python SDK to get the details for the target model.

```
# get model
import oci
from ads import set_auth
from oci.auth.signers import get_resource_principals_signer
from oci.data_science import DataScienceClient

set_auth(auth='resource_principal') 

resource_principal = get_resource_principals_signer() 
data_science_client = DataScienceClient(config={}, signer=resource_principal)

get_model_response = data_science_client.get_model(
    model_id="ocid1.datasciencemodel.oc1.iad.amaaaaaay75uckqare76rtyeaghvtsakscn2d6xscrvwyq7f6txc32742m3a")

# Get the data from response
print(get_model_response.data)

```
Refer [document](https://docs.oracle.com/en-us/iaas/tools/python-sdk-examples/2.162.0/datascience/get_model.py.html) for more details on get model SDK code.


2. Use the response from the **Get Model** call to update the custom_metadata_list within the **Update Model** Python SDK code. Specifically for changing the **deployment-container**, you must:

*  Change the value for the **custom_metadata_list** attribute with the key **deployment-container** to **odsc-vllm-serving**.
*  Copy all other **custom_metadata_list** attributes (key/value pairs) exactly as they appear in the **Get Model** response, ensuring no existing metadata is accidentally dropped during the update


```

import oci
from ads import set_auth
from oci.auth.signers import get_resource_principals_signer
from oci.data_science import DataScienceClient

set_auth(auth='resource_principal') 

resource_principal = get_resource_principals_signer() 
data_science_client = DataScienceClient(config={}, signer=resource_principal)

# Send the request to service, some parameters are not required, see API
# doc for more info
update_model_response = data_science_client.update_model(
    model_id="ocid1.datasciencemodel.oc1.iad.amaaaaaay75uckqare76rtyeaghvtsakscn2d6xscrvwyq7f6txc32742m3a",
    update_model_details=oci.data_science.models.UpdateModelDetails(
        custom_metadata_list=[
            oci.data_science.models.Metadata(
                category="Other",
                description="Deployment container mapping for SMC",
                key="deployment-container",
                value="odsc-vllm-serving",
                has_artifact=False),
        oci.data_science.models.Metadata(
                category="Other",
                description="Fine-tuning container mapping for SMC",
                key="finetune-container",
                value="odsc-llm-fine-tuning",
                has_artifact=False),
        oci.data_science.models.Metadata(
                category="Other",
                description="model by reference flag",
                key="modelDescription",
                value="true",
                has_artifact=False),
        oci.data_science.models.Metadata(
                category="Other",
                description="artifact location",
                key="artifact_location",
                value="oci://aqua-test-prod@idtlxnfdweil/custom-models/gemma-2b",
                has_artifact=False),
        oci.data_science.models.Metadata(
                category="Other",
                description="Evaluation container mapping for SMC",
                key="evaluation-container",
                value="odsc-llm-evaluate",
                has_artifact=False),]))

# Get the data from response
print(update_model_response.data)

```
Refer [document](https://docs.oracle.com/en-us/iaas/tools/python-sdk-examples/2.162.0/datascience/update_model.py.html) for more details on update model SDK code.

3. After updating the existing model, wait a short time for the changes to synchronize. Then, create a new model deployment; it will now launch the deployment using the **VLLM** container.



## Mitigation 2 - Re-register the above models using latest service managed model version 

1. Register the new model which uses the **VLLM** container (Refer to [register model](register-tips.md) document). 

After register the model after the service deprecates **TGI**, the above model will show **VLLM** container instead of **TGI**  
![Register model after tgi deprecation](web_assets/tgi-deprecation-after.png)

