# Overview

This repo provides two approaches to deploy LLM - 

* [Text Generation Inference](https://github.com/huggingface/text-generation-inference) from HuggingFace.
* [vLLM](https://github.com/vllm-project/vllm) developed at UC Berkeley 


The models are downloaded from the internet, so will require custom networking while creating model deployment.

# Model Deployment Steps

## Console 
1. Create file called token and paste your HF token into the file.
2. zip the token file as token.zip and upload to model catalog
3. To deploy using TGI, here are the startup parameters -
    a. For 7b parameter model use the following environment variables - 
    ```
    TOKEN_FILE=/opt/ds/model/deployed_model/token
    PARAMS="--model-id meta-llama/Llama-2-7b-chat-hf --max-batch-prefill-tokens 1024"
    ```
    b. For 13b parameter model use the following environment variables to run using VM.GPU.A10.2
    ```
    TOKEN_FILE=/opt/ds/model/deployed_model/token
    PARAMS="--model-id meta-llama/Llama-2-13b-chat-hf --max-batch-prefill-tokens 1024 --quantize bitsandbytes --max-batch-total-tokens 4096"
    STORAGE_SIZE_IN_GB=950
    ```
4. To deploy using TGI, here are the startup parameters -
    a. For 7b parameter model use the following environment variables - 
    ```
    TOKEN_FILE=/opt/ds/model/deployed_model/token
    PARAMS="--model meta-llama/Llama-2-7b-chat-hf"
    ```
5. Ports 5001 for both health and predict
6. CMD and Entrypoint blank
7. Choose custom networking and select vcn/subnet that has access to internet

## Using ADS

Refer to the ads-md-deploy-*.yaml for configurations

You can create a deployment by first creating a security token and then running one of:

### TGI

```
ads opctl run -f ads-md-deploy-tgi.yaml
```

### vLLM

```
ads opctl run -f ads-md-deploy-vllm.yaml
```

# Development

## TGI containers

`make build.tgi` to build the container

`make run.tgi` to run the container

`make shell.tgi` to launch container with shell prompt

`make stop.tgi` to stop the running container

## vLLM containers

`make build.vllm` to build the container

`make run.vllm` to run the container

`make shell.vllm` to launch container with shell prompt

`make stop.vllm` to stop the running container