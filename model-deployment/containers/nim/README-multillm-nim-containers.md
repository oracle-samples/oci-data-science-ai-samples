# Overview

This Readme walks through how to use NIM - [ Meta-Llama-3-8B-Instruct](https://huggingface.co/Undi95/Meta-Llama-3-8B-Instruct-hf) based container to deploy on OCI Data Science Model Deploy. This readme implements Multi llm NIM containers, in which you do not need to bring model specific images and a single image can host all supported LLMs.
Read more about Multi-LLM NIMs - [here](https://docs.nvidia.com/nim/large-language-models/latest/introduction.html)

* [llama3](https://github.com/meta-llama/llama3) from Meta.
* [NIM](https://catalog.ngc.nvidia.com/orgs/nim/teams/meta/containers/llama3-8b-instruct) by Nvidia

We describe two approaches to create this Model Deployment on OCI:
* Download Model using API-KEY from NGC Nvidia (described below)
* Utilising Object storage to store the model and creating a model catalog pointing to Object storage bucket [Refer](https://github.com/oracle-samples/oci-data-science-ai-samples/tree/main/model-deployment/containers/nim/README-MODEL-CATALOG.md)

## Prerequisites
* Access the corresponding NIM container llm. Click Get Container Button and click Request Access for NIM. At the time of writing this blog, you need a business email address to get access to NIM.
* For downloading this image from NGC catalog, you need to perform docker login to nvcr.io. Details of login information are mentioned on their [public doc](https://docs.nvidia.com/launchpad/ai/base-command-coe/latest/bc-coe-docker-basics-step-02.html).
Once logged in, we can directly pull image using -  
`docker pull nvcr.io/nim/nvidia/llm-nim:1.12.0`
* Generate API key to interact with NIM NGC APIs. [Reference document](https://org.ngc.nvidia.com/setup/api-key).
* Once the image is successfully pulled on your workstation, we will bring this image to Oracle Cloud Infrastructure Registry (OCIR). The necessary policies and process for OCIR interaction are mentioned in our [public docs](https://docs.oracle.com/en-us/iaas/data-science/using/mod-dep-byoc.htm).

## OCI Logging
When experimenting with new frameworks and models, it is highly advisable to attach log groups to model deployment in order to enable self assistance in debugging. Follow below steps to create log groups.

* Create logging for the model deployment (if you have to already created, you can skip this step)
  * Go to the [OCI Logging Service](https://cloud.oracle.com/logging/log-groups) and select `Log Groups`
  * Either select one of the existing Log Groups or create a new one
  * In the log group create ***two*** `Log`, one predict log and one access log, like:
    * Click on the `Create custom log`
    * Specify a name (predict|access) and select the log group you want to use
    * Under `Create agent configuration` select `Add configuration later`
    * Then click `Create agent configuration`


##### To directly get image from Nvidia NIM catalogue and upload to OCIR check: ```./README-SOURCE-NIM-TO-OCIR.MD```

## OCI Container Registry

* You need to `docker login` to the Oracle Cloud Container Registry (OCIR) first, if you haven't done so before been able to push the image. To login, you have to use your [API Auth Token](https://docs.oracle.com/en-us/iaas/Content/Registry/Tasks/registrygettingauthtoken.htm) that can be created under your `Oracle Cloud Account->Auth Token`. You need to login only once.

    ```bash
    docker login -u '<tenant-namespace>/<username>' <region>.ocir.io
    ```

  If `your tenancy` is **federated** with Oracle Identity Cloud Service, use the format `<tenancy-namespace>/oracleidentitycloudservice/<username>`

* Push the container image to the OCIR

    ```bash
    docker push <region>.ocir.io/<tenant-namespace>/`llm-nim:1.12.0`
    ```

## Deploy on OCI Data Science Model Deployment

Once you built and pushed the NIM container, you can now use the `Bring Your Own Container` Deployment in OCI Data Science to deploy the Llama3 model

### Creating Model catalog

Follow the steps mentioned [here](https://github.com/oracle-samples/oci-data-science-ai-samples/blob/main/model-deployment/containers/llama2/README.md#model-store-export-api-for-creating-model-artifacts-greater-than-6-gb-in-size)), refer the section One time download to OCI Model Catalog. 

We would utilise the above created model in the next steps to create the Model Deployment. 

### Create Model deploy

* To deploy the model now in the console, navigate to your [OCI Data Science Project](https://cloud.oracle.com/data-science/project)
  * Select the project created earlier and then select `Model Deployment`
  * Click on `Create model deployment`
  * Under `Default configuration` set following custom environment variables
      * Key: `MODEL_DEPLOY_PREDICT_ENDPOINT`, Value: `/v1/completions`
      * Key: `MODEL_DEPLOY_HEALTH_ENDPOINT`, Value: `/v1/health/ready`
      * Key: `NIM_SERVER_PORT`, Value: `8080`
      * Key: `SHM_SIZE`, Value: `10g`
      * Key: `NIM_MODEL_NAME`, Value: `/opt/ds/model/deployed_model`
      * Key: `OPENSSL_FORCE_FIPS_MODE`, Value: `0`
    * Under `Models` click on the `Select` button and select the Model Catalog entry we created earlier
    * Under `Compute` and then `Specialty and previous generation` select the `VM.GPU.A10.2` instance
    * Under `Networking` choose the `Default Networking` option.
    * Under `Logging` select the Log Group where you've created your predict and access log and select those correspondingly
    * Select the custom container option `Use a Custom Container Image` and click `Select`
    * Select the OCIR repository and image we pushed earlier
    * Leave the ports as the default port is 8080.
    * Leave CMD and Entrypoint as blank.
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
