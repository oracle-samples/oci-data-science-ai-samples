# Overview

This repo provides two approaches to deploy the Llama-2 LLM:

* [Text Generation Inference](https://github.com/huggingface/text-generation-inference) from HuggingFace.
* [vLLM](https://github.com/vllm-project/vllm) developed at UC Berkeley

The models are gated models, so they need to be requested access via Meta and Huggingface portals. Once access is granted and email communication has been received, we will create a model catalog item by following mentioned steps.

## Prerequisite

* Configure your [API Auth Token](https://docs.oracle.com/en-us/iaas/Content/Registry/Tasks/registrygettingauthtoken.htm) to be able to run and test your code locally
* Install [Docker](https://docs.docker.com/get-docker) or [Rancher Desktop](https://rancherdesktop.io/) as docker alternative

## Model Catalog Steps

* Download/Clone the model's repository that we are targetting to deploy, from huggingface repository.
     ```bash
    git lfs install
    git clone https://huggingface.co/meta-llama/Llama-2-13b-hf
    ```
* Zip all items of the folder using zip/tar utility, preferrably using below command to avoid creating another hierarchy of folder structure inside zipped file.
    ```bash
    zip <Filename>.zip * -0
    ```
* Upload the zipped artifact created in an object storage bucket in your tenancy. Tools like [rclone](https://rclone.org/), can help speed this upload. Using rclone with OCI can be referred from [here](https://docs.oracle.com/en/solutions/move-data-to-cloud-storage-using-rclone/configure-rclone-object-storage.html#GUID-8471A9B3-F812-4358-945E-8F7EEF115241)
* Next step is to create a model catalog item, using python script [create-large-modelcatalog.py](./create-large-modelcatalog.py). This script needs few inputs from users like Compartment OCID, Project OCID & Bucket details where we uploaded the model. There are multiple language SDK alternatives available as well, other than python.
* Depending on the size of the model, model catalog item will take time to be prepared before it can be utilised to be deployed using Model Deploy service. The script above will return the status SUCCEEDED, once the model is completely uploaded and ready to be used in Model Deploy service.

## Model Deployment Steps

Following outlines the steps needed to build the container which will be used for the deployment.

## Deploy with TGI

* Checkout this repository
* Enter the `model-deployment/containers/llama2-offline/tgi` folder:
* This example uses [OCI Container Registry](https://docs.oracle.com/en-us/iaas/Content/Registry/Concepts/registryoverview.htm) to store the container image required for the deployment. Open the `Makefile` and change the following variables placeholders to point to your Oracle Cloud Container Registry. Replace `<your-tenancy-name>` with the name of your tenancy, which you can find under your [account settings](https://cloud.oracle.com/tenancy) and the `region` with the 3 letter name of your tenancy region, you consider to use for this example, for example IAD for Ashburn, or FRA for Frankfurt. You can find the region keys in our public documentation for [Regions and Availability Domains](https://docs.oracle.com/en-us/iaas/Content/General/Concepts/regions.htm)

    ```bash
    export TENANCY_NAME=<your-tenancy-name>
    export REGION_KEY=<region-key>
    ```

* Build the deployment container image, this step would take awhile

    ```bash
    make build
    ```

* Before we can push the newly build container make sure that you've created the `text-generation-interface-odsc` repository in your tenancy.
  * Go to your tenancy [Container Registry](https://cloud.oracle.com/compute/registry/containers)
  * Click on the `Create repository` button
  * Select `Private` under Access types
  * Set `text-generation-interface-odsc` as a `Repository name`
  * Click on `Create` button

* You may need to `docker login` to the Oracle Cloud Container Registry (OCIR) first, if you haven't done so before been able to push the image. To login you have to use your [API Auth Token](https://docs.oracle.com/en-us/iaas/Content/Registry/Tasks/registrygettingauthtoken.htm) that can be created under your `Oracle Cloud Account->Auth Token`. You need to login only once.

    ```bash
    docker login -u '<tenant-namespace>/<username>' <region>.ocir.io
    ```

    If `your tenancy` is **federated** with Oracle Identity Cloud Service, use the format `<tenancy-namespace>/oracleidentitycloudservice/<username>`

* Push the container image to the OCIR

    ```bash
    make push
    ```

* Create logging for the model deployment, as an optional but helpful step
  * Go to the [OCI Logging Service](https://cloud.oracle.com/logging/log-groups) and select `Log Groups`
  * Either select one of the existing Log Groups or create a new one
  * In the log group create ***two*** `Log`, one predict log and one access log, like:
    * Click on the `Create custom log`
    * Specify a name (predict|access) and select the log group you want to use
    * Under `Create agent configuration` select `Add configuration later`
    * Then click `Create agent configuration`

* To deploy the model now in the console, go to back your [OCI Data Science Project](https://cloud.oracle.com/data-science/project)
  * Select the project you created earlier and than select `Model Deployment`
  * Click on `Create model deployment`
  * Models downloaded from model catalog, will be mounted and made avilable to the model server container at location: /opt/ds/model/deployed_model as part of Model Deploy BYOC contract. So under `Default configuration` set following custom environment variables
    * For `7b llama2` parameter model use the following environment variables
      * default PARAMS are going as `--max-batch-prefill-tokens 1024`, for custom requirement, set custom environment variable key `PARAMS` with value `--max-batch-prefill-tokens 1024` as needed.
    * For `13b llama2` parameter model use the following environment variables, notice this deployment uses quantization
      * set custom environment variable key `PARAMS` with value `--max-batch-prefill-tokens 1024 --quantize bitsandbytes --max-batch-total-tokens 4096`
    * Since TGI by default works on /generate for prediction endpoint, we need to map this custom endpoints to model deploy service oriented endpoint. We can achieve this by mentioning following environment variables in configuration section
      * Key: `MODEL_DEPLOY_PREDICT_ENDPOINT`, Value: `/generate`
    * Under `Models` click on the `Select` button and select the Model Catalog entry we created earlier
    * Under `Compute` and then `Specialty and previous generation` select the `VM.GPU.A10.2` instance
    * Under `Networking` leave the Default option
    * Under `Logging` select the Log Group where you've created your predict and access log and select those correspondingly
    * Click on `Show advanced options` at the bottom
    * Select the checkbox `Use a custom container image`
    * Select the OCIR repository and image we pushed earlier
    * No need to change port, as default port is mentioned 8080. But is is available as ENV variable in Dockerfile, so feel free to change as needed.
    * Leave CMD and Entrypoint blank
    * Click on `Create` button to create the model deployment

* Once the model is deployed and shown as `Active`, you can execute inference against it, the easier way to do it would be to use the integrated `Gradio` application in this example
  * Go to the model you've just deployed and click on it
  * Under the left side under `Resources` select `Invoking your model`
  * You will see the model endpoint under `Your model HTTP endpoint` copy it
  * Open the `config.yaml` file
  * Depending on which model you decided to deploy the 7b or 13b change the endpoint URL with the one you've just copied
  * Install the dependencies

    ```bash
    pip install gradio loguru
    ```

  * run the Gradio application with

    ```bash
    make app
    ```

    * You should be able to open the application now on your machine under `http://127.0.0.1:7861/` and use start chatting against the deployed model on OCI Data Science Service.

* Alternatively you can run inference against the deployed model with oci cli

```bash
oci raw-request --http-method POST --target-uri https://modeldeployment.eu-frankfurt-1.oci.customer-oci.com/ocid1.datasciencemodeldeployment.oc1.eu-frankfurt-1.amaaaaaan/predict --request-body '{"inputs":"Write a python program to randomly select item from a predefined list?","parameters":{"max_new_tokens":200}}' --auth resource_principal
```

## Deploy with vLLM
Container creation process is going to be same as TGI. All associated files are present in vllm directory. Once the container is pushed on OCIR, follow below steps:

* To deploy the model now in the console, go to back your [OCI Data Science Project](https://cloud.oracle.com/data-science/project)
  * Select the project you created earlier and than select `Model Deployment`
  * Click on `Create model deployment`
  * Models downloaded from model catalog, will be mounted and made avilable to the model server container at location: /opt/ds/model/deployed_model as part of Model Deploy BYOC contract. So under `Default configuration` set following custom environment variables
    * For `7b llama2` model, use the following environment variables
      * Default values in docker file are sufficient to handle the model deployment with tensor parallelism as 1
    * For `13b llama2` model, use the custom environment variable to override the default tensor parallelism as 2, to shard the model on 2 GPU cards.
      * Set custom environment variable key `TENSOR_PARALLELISM` with value `2`
    * Since in api server file, we have already changed the prediction endpoint to /predict, we don't need any other overrides.
    * Under `Models` click on the `Select` button and select the Model Catalog entry we created earlier
    * Under `Compute` and then `Specialty and previous generation` select the `VM.GPU.A10.2` instance
    * Under `Networking` leave the Default option
    * Under `Logging` select the Log Group where you've created your predict and access log and select those correspondingly
    * Click on `Show advanced options` at the bottom
    * Select the checkbox `Use a custom container image`
    * Select the OCIR repository and image we pushed earlier
    * No need to change port, as default port is mentioned 8080. But is is available as ENV variable in Dockerfile, so feel free to change as needed.
    * Leave CMD and Entrypoint blank
    * Click on `Create` button to create the model deployment

* Once the model is deployed and shown as `Active`, you can execute inference against it.

## Deploying using ADS

Instead of using the console, you can also deploy using the ADS from your local machine.

* make sure you have installed the ADS on your local machine

    ```bash
    python3 -m pip install oracle-ads
    ```

* refer to the `ads-md-deploy-*.yaml` for configurations and change with the OCIDs of the resources required for the deployment, like project ID, compartment ID etc. All of the configurations with `<UNIQUE_ID>` should be replaces with your corresponding ID from your tenancy, the resources we created in the previous steps.

Make sure that you've also created and setup your [API Auth Token](https://docs.oracle.com/en-us/iaas/Content/Registry/Tasks/registrygettingauthtoken.htm) to execute the commands below.

You can create a deployment by first creating a security token and then running one of:

### TGI

```bash
ads opctl run -f ads-md-deploy-tgi.yaml
```

### vLLM

```bash
ads opctl run -f ads-md-deploy-vllm.yaml
```

## Additional Make Commands

### TGI containers in TGI folder

`make build` to build the container

`make run` to run the container

`make push` to push the image

### vLLM containers in vllm folder

`make build` to build the container

`make run` to run the container

`make push` to push the image

## Gradio

Let's try the deployed model with Gradio

* install following libraries

    ```bash
    pip install gradio loguru
    ```
