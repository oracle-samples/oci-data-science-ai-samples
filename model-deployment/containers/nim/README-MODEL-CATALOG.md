# Overview

Utilising Model Catalog to store Models in OCI. We describe two ways to achieve this: 

* Storing zipped model file in Model Catalog
* Utilising Object storage to store the model and creating a model catalog pointing to Object storage bucket [Refer](https://github.com/oracle-samples/oci-data-science-ai-samples/tree/main/model-deployment/containers/nim/README-MODEL-CATALOG.md)

# Pre-requisite

The following are the pre-requisite:
* Notebook session with internet access (Recommended)
* Download the Llama 3 8B Instruct Model from [HuggingFace](https://huggingface.co/meta-llama/Meta-Llama-3-8B-Instruct) or NGC repository.

## Download NIM Container image and upload to OCIR
* Pull the latest NIM Image to local machine. Tag it with desired name.
    ```bash
    docker pull nvcr.io/nim/meta/llama3-8b-instruct:latest
    docker tag nvcr.io/nim/meta/llama3-8b-instruct:latest odsc-nim-llama3:latest 
    ```
## OCI Container Registry

Once NIM container is pushed, you can now use the `Bring Your Own Container` Deployment in OCI Data Science to deploy the Llama3 model.

# Method 1: Export Model to Model Catalog

Follow the steps mentioned [here](https://github.com/oracle-samples/oci-data-science-ai-samples/blob/main/model-deployment/containers/llama2/README.md#model-store-export-api-for-creating-model-artifacts-greater-than-6-gb-in-size)), refer the section One time download to OCI Model Catalog. 

We would utilise the above created model in the next steps to create the Model Deployment. 

# Method 2: Model-by-reference

Follow the steps to upload your model to Object Storage [here](https://github.com/oracle-samples/oci-data-science-ai-samples/blob/main/LLM/llama3.1-8B-deployment-vLLM-container.md#upload-model-to-oci-object-storage)

Utilise the [section](https://github.com/oracle-samples/oci-data-science-ai-samples/blob/main/LLM/llama3.1-8B-deployment-vLLM-container.md#create-model-by-reference-using-ads) on Create Model by Reference using ADS to create the model.

# ### Create Model deploy

* To deploy the model now in the console, navigate to your [OCI Data Science Project](https://cloud.oracle.com/data-science/project)
    * Select the project created earlier and then select `Model Deployment`
    * Click on `Create model deployment`
    * Under `Default configuration` set following custom environment variables
        * Key: `MODEL_DEPLOY_PREDICT_ENDPOINT`, Value: `/v1/completions`
        * Key: `MODEL_DEPLOY_HEALTH_ENDPOINT`, Value: `/v1/health/ready`
        * Key: `NIM_MODEL_NAME`, Value: `/opt/ds/model/deployed_model`
        * Key: `NIM_SERVER_PORT`, Value `8080`
        * Under `Models` click on the `Select` button and select the Model Catalog entry we created earlier
        * Under `Compute` and then `Specialty and previous generation` select the `VM.GPU.A10.1` instance
        * Under `Networking` choose the `Custom Networking` option and bring the VCN and subnet, which allows Internet access.
        * Under `Logging` select the Log Group where you've created your predict and access log and select those correspondingly
        * Click on `Show advanced options` at the bottom
        * Select the checkbox `Use a custom container image`
        * Select the OCIR repository and image we pushed earlier
        * Use port 8080.
        * Leave CMD and Entrypoint blank
        * Click on `Create` button to create the model deployment

* Once the model is deployed and shown as `Active`, you can execute inference against it.
    * Go to the model you've just deployed and click on it
    * Under the left side under `Resources` select `Invoking your model`
    * You will see the model endpoint under `Your model HTTP endpoint` copy it.

## Inference

  ```bash
  oci raw-request \
    --http-method POST \
    --target-uri <MODEL-DEPLOY-ENDPOINT> \
    --request-body '{"model": "/opt/ds/model/deployed_model", "messages": [ { "role":"user", "content":"Hello! How are you?" }, { "role":"assistant", "content":"Hi! I am quite well, how can I help you today?" }, { "role":"user", "content":"Can you write me a song?" } ], "top_p": 1, "n": 1, "max_tokens": 200, "stream": false, "frequency_penalty": 1.0, "stop": ["hello"] }' \
    --auth resource_principal
  ```

## Troubleshooting

[Reference](https://github.com/oracle-samples/oci-data-science-ai-samples/tree/main/model-deployment/containers/llama2#troubleshooting)

