# Overview

This repo provides two approaches to deploy the Llama-2 LLM:

* [Text Generation Inference](https://github.com/huggingface/text-generation-inference) from HuggingFace.
* [vLLM](https://github.com/vllm-project/vllm) developed at UC Berkeley

The models are downloaded from the internet during the deployment process, which requires custom networking setup while creating Oracle Cloud Infrastructure Data Science Model Deployment.

## Prerequisite

* Configure your [API Auth Token](https://docs.oracle.com/en-us/iaas/Content/Registry/Tasks/registrygettingauthtoken.htm) to be able to run and test your code locally
* Install [Docker](https://docs.docker.com/get-docker) or [Rancher Desktop](https://rancherdesktop.io/) as docker alternative

## Model Deployment Steps

Following outlines the steps needed to build the container which will be used for the deployment.

### Requirement

To construct the required containers for this deployment and retain the necessary information, please complete the following steps:

* checkout this repository
* enter the `llama2-model-deployment` folder:

    ```bash
    cd llama2-model-deployment/
    ```

* create a file called `token` in the same folder and store your Hugging Face user access token inside, which you can locate under your [Hugging Face Setting](https://huggingface.co/settings/tokens)

    ```bash
    echo 'your-huggingface-token-comes-here' >> token
    ```

* zip the `token` file we created in the earlier step

    ```bash
    zip token.zip token
    ```

* create an entry into the model catalog with your token key
  * open your [OCI Data Science Projects](https://cloud.oracle.com/data-science/projects/)
  * create a project if one does not exist yet
  * click on the project to enter it
  * from the left side under `Resources` select ***Models***
  * click on `Create model` button
  * specify a name, like `llama2-token`
  * under `Model artifact` click on the `Select` button and locate the `token.zip` file, then click `Upload`
  * click on `Create` to store the artifact

* create a subnet for the model deployment
  * go to the [Virtual Cloud Network](https://cloud.oracle.com/networking/vcns) in your Tenancy
  * select one of your existing VCNs
  * click on `Create subnet` button
  * specify a name
  * As `Subnet type` select `Regional`
  * as IP CIDR block set `10.0.32.0/19`
  * under `Route Table` select the routing table for private subnet
  * under `Subnet Access` select `Private Subnet`
  * click on `Create Subnet` to create it

* this example uses [OCI Container Registry](https://docs.oracle.com/en-us/iaas/Content/Registry/Concepts/registryoverview.htm) to store the container image required for the deployment. For the `Makefile` to execute the container build and push process to Oracle Cloud Container Registry, you have to setup in your local terminal the  `TENANCY_NAME` and `REGION_KEY` environment variables.`TENANCY_NAME` is the name of your tenancy, which you can find under your [account settings](https://cloud.oracle.com/tenancy) and the `REGION_KEY` is a 3 letter name of your tenancy region, you consider to use for this example, for example IAD for Ashburn, or FRA for Frankfurt. You can find the region keys in our public documentation for [Regions and Availability Domains](https://docs.oracle.com/en-us/iaas/Content/General/Concepts/regions.htm)

    ```bash
    export TENANCY_NAME=<your-tenancy-name>
    export REGION_KEY=<region-key>
    ```

## Deploy with TGI Container

* build the TGI container image, this step would take awhile

    ```bash
    make build.tgi
    ```

* before we can push the newly build container make sure that you've created the `text-generation-interface-odsc` repository in your tenancy.
  * Go to your tenancy [Container Registry](https://cloud.oracle.com/compute/registry/containers)
  * Click on the `Create repository` button
  * Select `Private` under Access types
  * Set `text-generation-interface-odsc` as a `Repository name`
  * Click on `Create` button

* you may need to `docker login` to the Oracle Cloud Container Registry (OCIR) first, if you haven't done so before been able to push the image. To login you have to use your [API Auth Token](https://docs.oracle.com/en-us/iaas/Content/Registry/Tasks/registrygettingauthtoken.htm) that can be created under your `Oracle Cloud Account->Auth Token`. You need to login only once.

    ```bash
    docker login -u '<tenant-namespace>/<username>' <region>.ocir.io
    ```

    If `your tenancy` is **federated** with Oracle Identity Cloud Service, use the format `<tenancy-namespace>/oracleidentitycloudservice/<username>`

* push the container image to the OCIR

    ```bash
    make push.tgi
    ```

* create logging for the model deployment
  * go to the [OCI Logging Service](https://cloud.oracle.com/logging/log-groups) and select `Log Groups`
  * either select one of the existing Log Groups or create a new one
  * in the log group create ***two*** `Log`, one predict log and one access log, like:
    * click on the `Create custom log`
    * specify a name (predict|access) and select the log group you want to use
    * under `Create agent configuration` select `Add configuration later`
    * then click `Create agent configuration`

## Deploy with vLLM Container

* build the vLLM container image, this step would take awhile

    ```bash
    make build.vllm
    ```

* before we can push the newly build container make sure that you've created the `vllm-odsc` repository in your tenancy.
  * Go to your tenancy [Container Registry](https://cloud.oracle.com/compute/registry/containers)
  * Click on the `Create repository` button
  * Select `Private` under Access types
  * Set `vllm-odsc` as a `Repository name`
  * Click on `Create` button

* you may need to `docker login` to the Oracle Cloud Container Registry (OCIR) first, if you haven't done so before been able to push the image. To login you have to use your [API Auth Token](https://docs.oracle.com/en-us/iaas/Content/Registry/Tasks/registrygettingauthtoken.htm) that can be created under your `Oracle Cloud Account->Auth Token`. You need to login only once.

    ```bash
    docker login -u '<tenant-namespace>/<username>' <region>.ocir.io
    ```

    If `your tenancy` is **federated** with Oracle Identity Cloud Service, use the format `<tenancy-namespace>/oracleidentitycloudservice/<username>`

* push the container image to the OCIR

    ```bash
    make push.vllm
    ```

* create logging for the model deployment
  * go to the [OCI Logging Service](https://cloud.oracle.com/logging/log-groups) and select `Log Groups`
  * either select one of the existing Log Groups or create a new one
  * in the log group create ***two*** `Log`, one predict log and one access log, like:
    * click on the `Create custom log`
    * specify a name (predict|access) and select the log group you want to use
    * under `Create agent configuration` select `Add configuration later`
    * then click `Create agent configuration`

## Deploy on OCI Data Science Model Deployment

Once you build and pushed the TGI or the vLLM container you can now use the Bring Your Own Container Deployment in OCI Data Science to the deploy the Llama2 model.

* to deploy the model now in the console, go to back your [OCI Data Science Project](https://cloud.oracle.com/data-science/project)
  * select the project you created earlier and than select `Model Deployment`
  * click on `Create model deployment`
  * under `Default configuration` set following custom environment variables
    * for `7b llama2` parameter model use the following environment variables
      * set custom environment variable key `TOKEN_FILE` with value `/opt/ds/model/deployed_model/token`
      * set custom environment variable key `PARAMS` with value `--model meta-llama/Llama-2-7b-chat-hf --tensor-parallel-size 4`
    * for `13b llama2` parameter model use the following environment variables, notice this deployment uses quantization
      * set custom environment variable key `TOKEN_FILE` with value `/opt/ds/model/deployed_model/token`
      * set custom environment variable key `PARAMS` with value `--model meta-llama/Llama-2-13b-chat-hf --tensor-parallel-size 4`
    * under `Models` click on the `Select` button and select the Model Catalog entry we created earlier with the `token.zip` file
    * under `Compute` and then `Specialty and previous generation` select the `VM.GPU.A10.2` instance
    * under `Networking` select the VCN and subnet we created in the previous step, specifically the subnet with the `10.0.0.0/19` CIDR
    * under `Logging` select the Log Group where you've created your predict and access log and select those correspondingly
    * click on `Show advanced options` at the bottom
    * select the checkbox `Use a custom container image`
    * select the OCIR repository and image we pushed earlier
    * select 5001 as ports for both health and predict
    * leave CMD and Entrypoint blank
    * click on `Create` button to create the model deployment

## Inference

* once the model is deployed and shown as `Active` you can execute inference against it, the easier way to do it would be to use the integrated `Gradio` application in this example
  * go to the model you've just deployed and click on it
  * under the left side under `Resources` select `Invoking your model`
  * you will see the model endpoint under `Your model HTTP endpoint` copy it
  * open the `config.yaml` file
  * depending on which model you decided to deploy the 7b or 14b change the endpoint URL with the one you've just copied
  * install the dependencies

    ```bash
    pip install -r requirements.txt
    ```

  * run the Gradio application with

    ```bash
    make app
    ```

    * you should be able to open the application now on your machine under `http://127.0.0.1:7861/` and use start chatting against the deployed model on OCI Data Science Service.

* alternatively you can run inference against the deployed model with oci cli from your OCI Data Science Notebook or you local environment

```bash
oci raw-request --http-method POST --target-uri https://modeldeployment.eu-frankfurt-1.oci.customer-oci.com/ocid1.datasciencemodeldeployment.oc1.eu-frankfurt-1.amaaaaaan/predict --request-body '{"inputs":"Write a python program to randomly select item from a predefined list?","parameters":{"max_new_tokens":200}}' --auth resource_principal
```

## Deploying using ADS

Instead of using the console, you can also deploy using the ADS from your local machine. Make sure that you've also created and setup your [API Auth Token](https://docs.oracle.com/en-us/iaas/Content/Registry/Tasks/registrygettingauthtoken.htm) to execute the commands below.

* make sure you have installed the ADS on your local machine

    ```bash
    python3 -m pip install oracle-ads
    ```

* refer to the `ads-md-deploy-*.yaml` for configurations and change with the OCIDs of the resources required for the deployment, like project ID, compartment ID etc. All of the configurations with `<UNIQUE_ID>` should be replaces with your corresponding ID from your tenancy, the resources we created in the previous steps.

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

### TGI containers

`make build.tgi` to build the container

`make run.tgi` to run the container

`make shell.tgi` to launch container with shell prompt

`make stop.tgi` to stop the running container

### vLLM containers

`make build.vllm` to build the container

`make run.vllm` to run the container

`make shell.vllm` to launch container with shell prompt

`make stop.vllm` to stop the running container

## Gradio

Let's try the deployed model with Gradio

* install following libraries

    ```bash
    pip install gradio loguru
    ```
