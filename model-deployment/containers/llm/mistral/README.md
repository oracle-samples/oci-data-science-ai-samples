# Overview

This repo provides two approaches to deploy the Mistral-7B LLM:

* [Text Generation Inference](https://github.com/huggingface/text-generation-inference) from HuggingFace.
* [vLLM](https://github.com/vllm-project/vllm) developed at UC Berkeley


## Prerequisites

* This is Limited Available feature. Please reach out to us via email `ask-oci-data-science_grp@oracle.com`  to ask to be allowlisted for this LA feature.
* Configure your [API Auth Token](https://docs.oracle.com/en-us/iaas/Content/Registry/Tasks/registrygettingauthtoken.htm) to be able to run and test your code locally.
* Install [Docker](https://docs.docker.com/get-docker) or [Rancher Desktop](https://rancherdesktop.io/) as docker alternative.

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

## Required IAM Policies

Public [documentation](https://docs.oracle.com/en-us/iaas/data-science/using/policies.htm).

### Generic Model Deployment policies
`allow group <group-name> to manage data-science-model-deployments in compartment <compartment-name>`

`allow dynamic-group <dynamic-group-name> to manage  data-science-model-deployments in compartment <compartment-name>`

### Allows a model deployment to emit logs to the Logging service. You need this policy if you’re using Logging in a model deployment
`allow any-user to use log-content in tenancy where ALL {request.principal.type = 'datasciencemodeldeployment'}`

### Model Store [export API](https://docs.oracle.com/en-us/iaas/data-science/using/large-model-artifact-export.htm#large-model-artifact-export) for creating model artifacts greater than 6 GB in size

`allow service datascience to manage object-family in compartment <compartment> where ALL {target.bucket.name='<bucket_name>'}`

`allow service objectstorage-<region> to manage object-family in compartment <compartment> where ALL {target.bucket.name='<bucket_name>'}`

### Policy to check Data Science work requests
`allow group <group_name> to manage data-science-work-requests in compartment <compartment_name>`

### Policy to access Model deployment end-point in Container Instance
`allow dynamic-group <group_name> to manage {DATA_SCIENCE_MODEL_DEPLOYMENT_PREDICT} in compartment <compartment_name>`

For all other Data Science policies, please refer these [details](https://github.com/oracle-samples/oci-data-science-ai-samples/blob/main/distributed_training/README.md#3-oci-policies).

## Methods for model weight downloads

### Direct Download

If you are choosing to download the model directly from HuggingFace repository at container startup time, you will need to configure a VCN with access to internet. Create a subnet for the model deployment
  * Go to the [Virtual Cloud Network](https://cloud.oracle.com/networking/vcns) in your Tenancy
  * Select one of your existing VCNs
  * Click on `Create subnet` button
  * Specify a name
  * As `Subnet type` select `Regional`
  * As IP CIDR block set `10.0.32.0/19`
  * Under `Route Table` select the routing table for private subnet
  * Under `Subnet Access` select `Private Subnet`
  * Click on `Create Subnet` to create it

The model will be downloaded at container startup time, we just need to provide authentication token to connect to model repository. Follow below steps to host the token:
* Create a file called `token` in the same folder and store your Hugging Face user access token inside, which you can locate under your [Hugging Face Setting](https://huggingface.co/settings/tokens)

    ```bash
    echo 'your-huggingface-token-comes-here' >> token
    ```

* Zip the `token` file we created in the earlier step

    ```bash
    zip token.zip token
    ```

* Create an entry into the model catalog with your token key
  * Open your [OCI Data Science Projects](https://cloud.oracle.com/data-science/projects/)
  * Create a project if one does not exist yet
  * Click on the project to enter it
  * From the left side under `Resources` select ***Models***
  * Click on `Create model` button
  * Specify a name, like `llama2-token`
  * Under `Model artifact` click on the `Select` button and locate the `token.zip` file, then click `Upload`
  * Click on `Create` to store the artifact

### One time download to OCI Model Catalog
* Download/Clone the model's repository that we are targetting to deploy, from huggingface repository. This can be done in Notebooks session for faster downloads and upload to bucket.
     ```bash
    git lfs install
    git clone https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.1
    ```
* Zip all items of the folder using zip/tar utility, preferrably using below command to avoid creating another hierarchy of folder structure inside zipped file.
    ```bash
    zip <Filename>.zip * -0
    ```
* Upload the zipped artifact created in an object storage bucket in your tenancy. Tools like [rclone](https://rclone.org/), can help speed this upload. Using rclone with OCI can be referred from [here](https://docs.oracle.com/en/solutions/move-data-to-cloud-storage-using-rclone/configure-rclone-object-storage.html#GUID-8471A9B3-F812-4358-945E-8F7EEF115241)
* Next step is to create a model catalog item, using python script [create-large-modelcatalog.py](./create-large-modelcatalog.py). This script needs few inputs from users like Compartment OCID, Project OCID & Bucket details where we uploaded the model. You can run this script either from Notebook session using resource principal, or using config file with user credentails with necessary policies. There are multiple language SDK alternatives available as well, other than python. The documentation of policies required to success execute this script, is mentioned in the python file.
    ```bash
    python create-large-modelcatalog.py
    ```
* Depending on the size of the model, model catalog item will take time to be prepared before it can be utilised to be deployed using Model Deploy service. The script above will return the status SUCCEEDED, once the model is completely uploaded and ready to be used in Model Deploy service.

## Build TGI or vLLM Containers
 
To build either TGI or vLLM image please refer [README.md](../inference-images/README.md)

## Deploy on OCI Data Science Model Deployment

Once you build and pushed the TGI or the vLLM container, you can now use the `Bring Your Own Container` Deployment in OCI Data Science to the deploy the Llama2 models.


### Deploy with TGI

* To deploy the model now in the console, go to back your [OCI Data Science Project](https://cloud.oracle.com/data-science/project)
  * Select the project you created earlier and than select `Model Deployment`
  * Click on `Create model deployment`
  * Models downloaded from model catalog, will be mounted and made avilable to the model server container at location: /opt/ds/model/deployed_model as part of Model Deploy BYOC contract. So under `Default configuration` set following custom environment variables
    * Since TGI by default works on /generate for prediction endpoint, we need to map this custom endpoints to model deploy service oriented endpoint. We can achieve this by mentioning following environment variables in configuration section
      * Key: `MODEL_DEPLOY_PREDICT_ENDPOINT`, Value: `/generate`
    * If you are downloading models directly from source, we will need these additional environment variable configurations:
      * Set custom environment variable key `TOKEN_FILE` with value `/opt/ds/model/deployed_model/token`, as the token will be available at this path.
      * Set custom environment variable key `MODEL` with value `mistralai/Mistral-7B-Instruct-v0.1`, this is the model that will be downloaded during container start.
      * Set custom environment variable key `STORAGE_SIZE_IN_GB` with value `950` for 7b model. This is required as model will be downloaded at runtime, so we need to keep extra storage size to accomodate various model sizes.
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
oci raw-request --http-method POST --target-uri https://<MD_OCID>/predict  --request-body '{"inputs":"Tell me about Data Science","parameters":{"max_new_tokens":20}}'
```

### Deploy with vLLM
Model Catalog steps will be common for vLLM. Users can use python script [create-large-modelcatalog.py](./create-large-modelcatalog.py) and execute as a python excutable after inputting required values like compartment OCID, project OCID and source bucket details.
Container creation process is going to be same as TGI. All associated files are present in vllm directory. Once the container is pushed on OCIR, follow below steps:

* To deploy the model now in the console, go to back your [OCI Data Science Project](https://cloud.oracle.com/data-science/project)
  * Select the project you created earlier and than select `Model Deployment`
  * Click on `Create model deployment`
  * Models downloaded from model catalog, will be mounted and made avilable to the model server container at location: /opt/ds/model/deployed_model as part of Model Deploy BYOC contract. So under `Default configuration` set following custom environment variables
    * To use `vLLm as Openai-Compatible server`  model, use the following environment variables
      * Since vLLm is being deployed as a server that mimics the OpenAI API protocol, by default it works on /v1/completions for prediction endpoint, we need to map this custom endpoints to model deploy service oriented endpoint. We can achieve this by mentioning following environment variables in configuration section
        * Key: `MODEL_DEPLOY_PREDICT_ENDPOINT`, Value: `/v1/completions`
      * Set custom environment variable key `API_SPEC` with value `openai`

    * If you are downloading models directly from source, we will need these additional environment variable configurations:
      * Set custom environment variable key `TOKEN_FILE` with value `/opt/ds/model/deployed_model/token`, as the token will be available at this path.
      * Set custom environment variable key `MODEL` with value `mistralai/Mistral-7B-Instruct-v0.1`, this is the model that will be downloaded during container start.
      * Set custom environment variable key `STORAGE_SIZE_IN_GB` with value `950` for 7b model. This is required as model will be downloaded at runtime, so we need to keep extra storage size to accomodate various model sizes.
    * Since in api server file, we have already changed the prediction endpoint to /predict, we don't need any other overrides.
    * Under `Models` click on the `Select` button and select the Model Catalog entry we created earlier
    * Under `Compute` and then `Specialty and previous generation` select the `VM.GPU.A10.2` instance
    * Under `Networking` leave the Default option
    * Under `Logging` select the Log Group where you've created your predict and access log and select those correspondingly
    * Click on `Show advanced options` at the bottom
    * Select the checkbox `Use a custom container image`
    * Select the OCIR repository and image we pushed earlier
    * To use vLLM as OpenAI-compatible server we need to mention the healthcheck port.
     * Key: `healthCheckPort`, Value: 5002
      No need to change port for running vLLM as default server, as default port is mentioned 8080. But is is available as ENV variable in Dockerfile, so feel free to change as needed.
    * Leave CMD and Entrypoint blank
    * Click on `Create` button to create the model deployment

* Once the model is deployed and shown as `Active`, you can execute inference against it.
```bash
oci raw-request --http-method POST --target-uri https://<MD_OCID>/predict --request-body '{"inputs": "Tell me about Data Science"}'
```
  To execute OpenAI-compatible inference, you can run below command.
  ```bash
oci raw-request --http-method POST --target-uri https://<MD_OCID>/predict --request-body '{"model": "/opt/ds/model/deployed_model",
        "prompt":"what are some good skills deep learning expert. Give us some tips on how to structure interview with some coding example?",
        "max_tokens":250, 
        "temperature": 0.7,
        "top_p":0.8}'
```

## Inference

### Local Inference

* Once the model is deployed and shown as `Active` you can execute inference against it, the easier way to do it would be to use the integrated `Gradio` application in this example
  * Go to the model you've just deployed and click on it
  * Under the left side under `Resources` select `Invoking your model`
  * You will see the model endpoint under `Your model HTTP endpoint` copy it
  * Open the `config.yaml` file
  * Change the endpoint URL for the model with the one you've just copied
  * Install the dependencies

    ```bash
    pip install -r requirements.txt
    ```

  * Run the Gradio application with

    ```bash
    make app
    ```

    * You should be able to open the application now on your machine under `http://127.0.0.1:7861/` and use start chatting against the deployed model on OCI Data Science Service.

* Alternatively you can run inference against the deployed model with oci cli from your OCI Data Science Notebook or you local environment

  * TGI Inference

    ```bash
    oci raw-request \
      --http-method POST \
      --target-uri "https://modeldeployment.us-ashburn-1.oci.customer-oci.com/ocid1.datasciencemodeldeployment.oc1.iad.amaaaaaav66vvniam45ujbnig43wiltlf6h2p4ohrauk7kq5tspnn427pkra/predict" \
      --request-body '{
        "inputs": "Write a python program to randomly select item from a predefined list?",
        "parameters": {
          "max_new_tokens": 200
        }
      }' \
      --auth resource_principal
    ```

  * vLLM Inference
  
    * OpenAI compatible server
    ```bash
    oci raw-request 
    --http-method POST 
    --target-uri "https://modeldeployment.us-ashburn-1.oci.customer-oci.com/ocid1.datasciencemodeldeployment.oc1.iad.amaaaaaav66vvniabq7ahm2h2pbvh6ti37svti5n5fk7jirucxdtdfcuo22q/predict"
    --request-body '{"model": "/opt/ds/model/deployed_model",
        "prompt":"what are some good skills deep learning expert. Give us some tips on how to structure interview with some coding example?",
        "max_tokens":250, 
        "temperature": 0.7,
        "top_p":0.8}'
    ```

  ### Using OCI Container Instance
   
  * Once you have tested the inference locally. You can build Gradio container by running:
    ```bash
    make build.app
    ```
  * Before we can push the newly build container make sure that you've created the `gradio-odsc` repository in your tenancy.
  * Go to your tenancy [Container Registry](https://cloud.oracle.com/compute/registry/containers)
  * Click on the `Create repository` button
  * Select `Private` under Access types
  * Set `gradio-odsc` as a `Repository name`
  * Click on `Create` button

* You may need to `docker login` to the Oracle Cloud Container Registry (OCIR) first, if you haven't done so before been able to push the image. To login you have to use your [API Auth Token](https://docs.oracle.com/en-us/iaas/Content/Registry/Tasks/registrygettingauthtoken.htm) that can be created under your `Oracle Cloud Account->Auth Token`. You need to login only once.

    ```bash
    docker login -u '<tenant-namespace>/<username>' <region>.ocir.io
    ```

    If `your tenancy` is **federated** with Oracle Identity Cloud Service, use the format `<tenancy-namespace>/oracleidentitycloudservice/<username>`

* Push the container image to the OCIR

    ```bash
    make push.app
    ```
* To run a Container Instance go to [Container Instance](https://console.us-ashburn-1.oraclecloud.com/container-instances)
    * Click on the `Create container instance`
    * Select the compartment in `Create in compartment` option
    * Leave `Placement` and `Shape` as default option
    * Within `Network` select your `Virtual cloud network` and `Subnet`
    * Click on `Next` at the bottom, it redirects to `Configure containers` page
    * Select the OCIR repository and image we pushed earlier under `Image`
    * Provide custom ENV variable for Gradio app in `Environmental variables` section
      * Key: `PORT`, Value: `5000` (Port at which you want to run the app)\
      * Key: `MODEL`, Value: `mistralai/Mistral-7B-Instruct-v0.1`
      * Key: `OCI_IAM_TYPE`, Value: `resource_principal`
      * Key: `VLLM`, Value: `1` (For VLLM Inference end-point)
      * Key: `API_SPEC` Value: `openai` (For VLLM OpenAI Inference end-point)
    * Click on `Next` at the bottom to review the configuration and then click `Create`

* Once container is up you should be able to open the application now on `http://<Private IP address>:<PORT>/` and use start chatting against the deployed model on OCI Data Science Service.

## Deploying using ADS

Instead of using the console, you can also deploy using the ADS from your local machine. Make sure that you've also created and setup your [API Auth Token](https://docs.oracle.com/en-us/iaas/Content/Registry/Tasks/registrygettingauthtoken.htm) to execute the commands below.

* Make sure you have installed the ADS on your local machine

    ```bash
    python3 -m pip install oracle-ads
    ```

* Refer to the `ads-md-deploy-*.yaml` for configurations and change with the OCIDs of the resources required for the deployment, like project ID, compartment ID etc. All of the configurations with `<UNIQUE_ID>` should be replaces with your corresponding ID from your tenancy, the resources we created in the previous steps.

You can create a deployment by first creating a security token and then running one of:

### TGI

```bash
ads opctl run -f ads-md-deploy-tgi.yaml
```

### vLLM

```bash
ads opctl run -f ads-md-deploy-vllm.yaml
```

## Troubleshooting

Following are identified as the most probable failure cases while deploying large models.

### Create/Update Model deployment failure

#### Reason
Insufficient model deployment timeout.

#### Symptom
The Work Request logs will show the following error:
Workflow timed out. Maximum runtime was: <deployment_timeout> minutes.

#### Mitigation
If model loading takes more time than service calculated, user can override deployment timeout with default configuration override by using below key value pair
`DEPLOYMENT_TIMEOUT_IN_MINUTES`: `60`

Max value allowed is 240

### Create/Update Model deployment failure

#### Reason
Insufficient boot volume storage.

#### Symptoms
The Work Request logs will show the following error: Errors occurred while bootstrapping the Model Deployment.
The customer should investigate further to determine that the failure was due to lack of sufficient boot volume size.

#### Mitigation
If model zip compression rate is too high and service failed to download and unzip the artifact, user can override volume size with default configuration override by using below key value pair.
`STORAGE_SIZE_IN_GB`: `1000`

Max value allowed as high as max boot volumes allowed.

### Create/Update Model deployment failure

#### Reason
Container timeout.

#### Symptoms
The Work Request logs will show the following error: Errors occurred while bootstrapping the Model Deployment

#### Mitigation
Customer should check the predict and health check endpoints, if defined through environment variables, are valid for container image specified. They can also check the predict and access logs for more information.

### Advanced debugging options: Code debugging inside the container using job
For more detailed level of debugging, user can refer [README-DEBUG.md](./README-DEBUG.md).

