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

* create logging for the model deployment (if you have to already created, you can skip this step)
  * go to the [OCI Logging Service](https://cloud.oracle.com/logging/log-groups) and select `Log Groups`
  * either select one of the existing Log Groups or create a new one
  * in the log group create ***two*** `Log`, one predict log and one access log, like:
    * click on the `Create custom log`
    * specify a name (predict|access) and select the log group you want to use
    * under `Create agent configuration` select `Add configuration later`
    * then click `Create agent configuration`

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

You can find the official documentation about OCI Data Science Model Deployment: [https://docs.oracle.com/en-us/iaas/data-science/using/model_dep_create.htm]

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

## Deploy with vLLM Container

You can find the official documentation about OCI Data Science Model Deployment: [https://docs.oracle.com/en-us/iaas/data-science/using/model_dep_create.htm]

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

## Deploy on OCI Data Science Model Deployment

Once you build and pushed the TGI or the vLLM container you can now use the Bring Your Own Container Deployment in OCI Data Science to the deploy the Llama2 model.

* to deploy the model now in the console, go back your [OCI Data Science Project](https://cloud.oracle.com/data-science/project)
  * select the project you created earlier and than select `Model Deployment`
  * click on `Create model deployment`
  * `TGI Container` deployment
    * under `Default configuration` set following custom environment variables
      * for `7b llama2` parameter model use the following environment variables
        * set custom environment variable key `TOKEN_FILE` with value `/opt/ds/model/deployed_model/token`
        * set custom environment variable key `PARAMS` with value `--model-id meta-llama/Llama-2-7b-chat-hf --max-batch-prefill-tokens 1024`
      * for `13b llama2` parameter model use the following environment variables, notice this deployment uses quantization
        * set custom environment variable key `TOKEN_FILE` with value `/opt/ds/model/deployed_model/token`
        * set custom environment variable key `PARAMS` with value `--model meta-llama/Llama-2-13b-chat-hf --max-batch-prefill-tokens 1024 --quantize bitsandbytes --max-batch-total-tokens 4096`
  * `vLLM Container` deployment
    * under `Default configuration` set following custom environment variables
      * for `7b llama2` parameter model use the following environment variables
        * set custom environment variable key `TOKEN_FILE` with value `/opt/ds/model/deployed_model/token`
        * set custom environment variable key `PARAMS` with value `--model meta-llama/Llama-2-7b-chat-hf`
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

  * TGI Inference

    ```bash
    oci raw-request \
      --http-method POST \
      --target-uri "https://modeldeployment.eu-frankfurt-1.oci.customer-oci.com/ocid1.datasciencemodeldeployment.oc1.eu-frankfurt-1.amaaaaaanif7xwiahljboucy47byny5xffyc3zbkpfk4jtcdrtycjb6p2tsa/predict" \
      --request-body '{
        "inputs": "Write a python program to randomly select item from a predefined list?",
        "parameters": {
          "max_new_tokens": 200
        }
      }' \
      --auth resource_principal
    ```

  * vLLM Inference

    ```bash
    oci raw-request \
      --http-method POST \
      --target-uri "https://modeldeployment.eu-frankfurt-1.oci.customer-oci.com/ocid1.datasciencemodeldeployment.oc1.eu-frankfurt-1.amaaaaaanif7xwiaje3uc4c5igep2ppcefnyzuab3afufefgepicpl5whm6q/predict" \
      --request-body '{
        "prompt": "are you smart?",
        "use_beam_search": true,
        "n": 4,
        "temperature": 0
      }' \
      --auth resource_principal
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

## Debugging

You could debug the code in the container utilizing the [Visual Studio Code Remote - Tunnels](https://code.visualstudio.com/docs/remote/tunnels) extension, which lets you connect to a remote machine, like a desktop PC or virtual machine (VM), via a secure tunnel. You can connect to that machine from a VS Code client anywhere, without the requirement of setting up your own SSH, including also using the Oracle Cloud Infrastructure Data Science Jobs.

The tunneling securely transmits data from one network to another. This can eliminate the need for the source code to be on your VS Code client machine since the extension runs commands and other extensions directly on the OCI Data Science Job remote machine.

### Requirements

To use the debugging you have to finalize the steps of building and pushing the container of your choice to the Oracle Cloud Container Registry.

## Run for Debugging

For debugging purposes we will utilize the OCI Data Science Jobs service. Once the TGI or the vLLM container was build and published to the OCIR, we can run it as a Job, which would enable us take advance of the VSCode Remote Tunneling. To do so follow the steps:

* in your [OCI Data Science](https://cloud.oracle.com/data-science/projects) section, select the project you've created for deployment
* under the `Resources` section select `Jobs`
* click on `Create job` button
* under the `Default Configuration` select the checkbox for `Bring your own container`
  * set following environment variables:
  * `CONTAINER_CUSTOM_IMAGE` with the value to the OCI Container Registry Repository location where you pushed your container, for example: `<your-region>.ocir.io/<your-tenancy-name>/vllm-odsc:0.1.3`
  * `CONTAINER_ENTRYPOINT` with the value `"/bin/bash", "--login",  "-c"`
  * `CONTAINER_CMD` with the value `/aiapps/runner.sh`
  * the above values will override the default values set in the `Dockerfile` and would enable to launch the tunneling
* under `Compute shape` select `Custom configuration` and then `Specialty and previous generation` and select the `VM.GPU.A10.2` shape
* under `Logging` select the log group you've created for the model deployment and keep the option `Enable automatic log creation`
* under `Storage` set 500GB+ of storage
* under `Networking` keep the `Default networking` configuration

With this we are now ready to start the job

* select the newly created job, if you have not done so
* click on the `Start a job run` 
* keep all settings by default and click on `Start` button at the bottom left

Once the job is up and running, you will notice in the logs, the authentication code appears, you can copied and use it to authorize the tunnel, few seconds later the link for the tunnel would appear.

![vscode tunnel in the oci job](../../../jobs/tutorials/assets/images/vscde-server-tunnel-job.png)

Copy the link and open it in a browser, which should load the VSCode Editor and reveals the code inside the job, enabling direct debugging and coding.

`Notice` that you can also use your local VSCode IDE for the same purpose via the [Visual Studio Code Remote - Tunnels](https://code.visualstudio.com/docs/remote/tunnels) extension

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
