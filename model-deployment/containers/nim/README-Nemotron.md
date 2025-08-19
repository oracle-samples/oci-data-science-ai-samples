# Overview

The NVIDIA Nemotron family of multimodal models provides state-of-the-art agentic reasoning for graduate-level scientific reasoning, advanced math, coding, instruction following, tool calling, and visual reasoning. Nemotron models excel in vision for enterprise optical character recognition (OCR) and in reasoning for building agentic AI.
In this guide, we are going to deploy [Mistral-Nemo-12B-Instruct](https://catalog.ngc.nvidia.com/orgs/nim/teams/nv-mistralai/containers/mistral-nemo-12b-instruct) on OCI Data Science.


## Prerequisites
* Access the corresponding NIM container llm. Click Get Container Button and click Request Access for NIM. At the time of writing this blog, you need a business email address to get access to NIM.
* For downloading this image from NGC catalog, you need to perform docker login to nvcr.io. Details of login information are mentioned on their [public doc](https://docs.nvidia.com/launchpad/ai/base-command-coe/latest/bc-coe-docker-basics-step-02.html).
Once logged in, we can directly pull image using -  
`docker pull nvcr.io/nim/nv-mistralai/mistral-nemo-12b-instruct:1.2`
* Generate API key to interact with NIM NGC APIs. [Reference document](https://org.ngc.nvidia.com/setup/api-key).
* Once the image is successfully pulled on your workstation, we will bring this image to Oracle Cloud Infrastructure Registry (OCIR). The necessary policies and process for OCIR interaction are mentioned in our [public docs](https://docs.oracle.com/en-us/iaas/data-science/using/mod-dep-byoc.htm).
* For model - mistral-nemo-12b-instruct, we will be using A10.2 GPU shape. Depending on the region, user may need a reservation request to secure the VM. 

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
    docker push <region>.ocir.io/<tenant-namespace>/`mistral-nemo-12b-instruct:1.2`
    ```

## Deploy on OCI Data Science Model Deployment

Once you built and pushed the NIM container, you can now use the `Bring Your Own Container` Deployment in OCI Data Science to deploy the mistral-nemo-12b-instruct model.

### Creating Model catalog

Create a dummy model catalog entry to link it with a model deployment using any zip file.
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
      * Key: `OPENSSL_FORCE_FIPS_MODE`, Value: `0`
      * Key: `NGC_API_KEY`, Value: `<NGC KEY>`
      * Key: `WEB_CONCURRENCY`, Value: `1`
      * Key: `NCCL_CUMEM_ENABLE`, Value: `0`
      * Key: `NIM_MAX_MODEL_LEN`, Value: `4000` Note: Can be increased based on instance shape used
    * Under `Models` click on the `Select` button and select the Model Catalog entry we created earlier
    * Under `Compute` and then `Specialty and previous generation` select the `VM.GPU.A10.2` instance
    * Under `Networking` choose the `Custom Networking` option and bring the VCN and subnet, which allows Internet access.
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
    --request-body '{"model": "mistral-nemo-12b-instruct", "messages": [ { "role":"user", "content":"Hello! How are you?" }, { "role":"assistant", "content":"Hi! I am quite well, how can I help you today?" }, { "role":"user", "content":"Can you write me a song?" } ], "top_p": 1, "n": 1, "max_tokens": 200, "stream": false, "frequency_penalty": 1.0, "stop": ["hello"] }' \
    --auth resource_principal
  ```

## Troubleshooting

[Reference](https://github.com/oracle-samples/oci-data-science-ai-samples/tree/main/model-deployment/containers/llama2#troubleshooting)
