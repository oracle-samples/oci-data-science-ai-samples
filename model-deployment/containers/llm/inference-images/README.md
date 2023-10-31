# Overview

This repo provides two approaches to manage the inference server for LLM deployment in OCI Data Science:

* [Text Generation Inference](https://github.com/huggingface/text-generation-inference) from HuggingFace.
* [vLLM](https://github.com/vllm-project/vllm) developed at UC Berkeley

## Prerequisites

* This is Limited Available feature. Please reach out to us via email `ask-oci-data-science_grp@oracle.com`  to ask to be allowlisted for this LA feature.
* Configure your [API Auth Token](https://docs.oracle.com/en-us/iaas/Content/Registry/Tasks/registrygettingauthtoken.htm) to be able to run and test your code locally.
* Install [Docker](https://docs.docker.com/get-docker) or [Rancher Desktop](https://rancherdesktop.io/) as docker alternative.

## Required IAM Policies

Public [documentation](https://docs.oracle.com/en-us/iaas/data-science/using/policies.htm).

### Bring your own container [policies](https://docs.oracle.com/en-us/iaas/data-science/using/model-dep-policies-auth.htm#model_dep_policies_auth__access-logging-service#model_dep_policies_auth__access-custom-container)
`ALL { resource.type = 'datasciencemodeldeployment' }`

`allow dynamic-group <dynamic-group-name> to read repos in compartment <compartment-name> where ANY {request.operation='ReadDockerRepositoryMetadata',request.operation='ReadDockerRepositoryManifest',request.operation='PullDockerLayer' }`

#### If the repository is in the root compartment, allow read for the tenancy

`allow dynamic-group <dynamic-group-name> to read repos in tenancy where ANY {
    request.operation='ReadDockerRepositoryMetadata',
    request.operation='ReadDockerRepositoryManifest',
    request.operation='PullDockerLayer'
}`

#### For user level policies

`allow any-user to read repos in tenancy where ALL { request.principal.type = 'datasciencemodeldeployment' }`

`allow any-user to read repos in compartment <compartment-name> where ALL { request.principal.type = 'datasciencemodeldeployment'}`

For all other Data Science policies, please refer these [details](https://github.com/oracle-samples/oci-data-science-ai-samples/blob/main/distributed_training/README.md#3-oci-policies).

## Build TGI Container
To construct the required containers for this deployment and retain the necessary information, please complete the following steps:

* Checkout this repository
* Enter the path `model-deployment/containers/llm/inference-images`

    ```bash
    cd model-deployment/containers/llm/inference-images
    ```
* This example uses [OCI Container Registry](https://docs.oracle.com/en-us/iaas/Content/Registry/Concepts/registryoverview.htm) to store the container image required for the deployment. For the `Makefile` to execute the container build and push process to Oracle Cloud Container Registry, you have to setup in your local terminal the  `TENANCY_NAME` and `REGION_KEY` environment variables.`TENANCY_NAME` is the name of your tenancy, which you can find under your [account settings](https://cloud.oracle.com/tenancy) and the `REGION_KEY` is a 3 letter name of your tenancy region, you consider to use for this example, for example IAD for Ashburn, or FRA for Frankfurt. You can find the region keys in our public documentation for [Regions and Availability Domains](https://docs.oracle.com/en-us/iaas/Content/General/Concepts/regions.htm)

    ```bash
    export TENANCY_NAME=<your-tenancy-name>
    export REGION_KEY=<region-key>
    ```

You can find the official documentation about OCI Data Science Model Deployment: [https://docs.oracle.com/en-us/iaas/data-science/using/model_dep_create.htm]

* Build the TGI container image, this step would take awhile

    ```bash
    make build.tgi
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
    make push.tgi
    ```

## Build vLLM Container

You can find the official documentation about OCI Data Science Model Deployment: [https://docs.oracle.com/en-us/iaas/data-science/using/model_dep_create.htm]

* Build the vLLM container image, this step would take awhile

    ```bash
    make build.vllm
    ```

* Before we can push the newly build container make sure that you've created the `vllm-odsc` repository in your tenancy.
  * Go to your tenancy [Container Registry](https://cloud.oracle.com/compute/registry/containers)
  * Click on the `Create repository` button
  * Select `Private` under Access types
  * Set `vllm-odsc` as a `Repository name`
  * Click on `Create` button

* You may need to `docker login` to the Oracle Cloud Container Registry (OCIR) first, if you haven't done so before been able to push the image. To login you have to use your [API Auth Token](https://docs.oracle.com/en-us/iaas/Content/Registry/Tasks/registrygettingauthtoken.htm) that can be created under your `Oracle Cloud Account->Auth Token`. You need to login only once.

    ```bash
    docker login -u '<tenant-namespace>/<username>' <region>.ocir.io
    ```

    If `your tenancy` is **federated** with Oracle Identity Cloud Service, use the format `<tenancy-namespace>/oracleidentitycloudservice/<username>`

* Push the container image to the OCIR

    ```bash
    make push.vllm
    ```



### Advanced debugging options: Code debugging inside the container using job
For more detailed level of debugging, user can refer [README-DEBUG.md](./README-DEBUG.md).

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
