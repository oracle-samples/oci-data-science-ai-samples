# Overview

In this demo you will learn how to run a multi node distributed fine tuning of Large language model and deploy the fine tuned model using OCI Data Science service. We will use llama2-recipe github repo for the distributed training code. 
The number of parameter is 13b. You can use any of the model size of your choice in your implementation. The key objective of the fine tuning task is to summarize dialog/conversation.


# References

* https://github.com/facebookresearch/llama-recipes/tree/main
* https://accelerated-data-science.readthedocs.io/en/latest/user_guide/model_training/training_llm.html
* https://huggingface.co/datasets/samsum/viewer/samsum/test?row=11

# Prerequisite

* OCI Preview SDK with support for mounted storage volume in jobs
* latest version of oracle-ads - `pip install oracle-ads[opctl] -U`
* Allow list the tenancy for mounted storage volume
* Object storage bucket to save the fine tuned weights 
* policies to allow jobrun and notebook to access the object storage buckets
* Access token from Huggingface to download llama2 model
* Log group and log from logging service. This will be used to monitor the progress of the training
* Custom Subnet with security list to allow ingress into any port from the IPs originating within the CIDR block of the subnet. This is to ensure that the hosts on the subnet can connect to each other during distributed training. 

# Data Science Resources

* Notebook session - We will use this for initiating the distributed training and to access the fine tuned weights
* Data Science Jobs - Used for distributed training
* Model Deployment - For deploying the fine tuned model on OCI Data Science


# Creating Job run

We will use VM.GPU.A10.2 shape instances. This shape provides 2 A10 cards. We will use 6 instances, with total of 12 cards to train 13 billion parameter model.

Prepare a yaml file that describes the infrastructure and the job parameters. Use the template below and customize it with the resource IDs under infrastructure block. The shape name provided should be an instance with A10 or A100. Save the yaml file as `llama2-ft-job.yaml`

You can configure the number of nodes by changing the `replicas` attribute under `runtime` spec.

With 6 nodes and 13b parameter model, it will take about 2.5 hours to complete 3 epochs. 

```

kind: job
apiVersion: v1.0
spec:
  name: LLAMA2-Fine-Tuning-lora-samsum-13b
  infrastructure:
    kind: infrastructure
    spec:
      blockStorageSize: 256
      compartmentId: ocid1.compartment.oc1..xxxxxxxxxxxxxxxxxxxxxx
      logGroupId: ocid1.loggroup.oc1.xx-xxx.xxxxxxxxxxxxxxxxxx
      logId: ocid1.log.oc1.xxx.xxxxxxxxxxxxxxxxxxx
      projectId: ocid1.datascienceproject.oc1.xxx.xxxxxxxxxxxxxxx
      subnetId: ocid1.subnet.oc1.xxx.xxxxxxxxxxxxxxxxxxxxxxxx
      shapeName: VM.GPU.A10.2
      storageMount:
      - dest: outputs
        src: oci://<bucket-to-save-finetuned-weights>@<namespace>/llama2-ft-lora-13b/
    type: dataScienceJob
  runtime:
    kind: runtime
    type: pyTorchDistributed
    spec:
      git:
        url: https://github.com/facebookresearch/llama-recipes.git
      command: >-
        torchrun examples/finetuning.py
        --enable_fsdp
        --use_peft
        --peft_method lora
        --pure_bf16
        --mixed_precision
        --batch_size_training 4
        --model_name meta-llama/Llama-2-13b-hf
        --output_dir /mnt/outputs
        --num_epochs 3 
        --save_model 
      replicas: 6
      conda:
        type: service
        slug: pytorch20_p39_gpu_v2
      dependencies:
        pipPackages: >-
          'accelerate>=0.21.0'
          appdirs
          loralib
          bitsandbytes==0.39.1
          black
          'black[jupyter]'
          datasets
          fire
          'git+https://github.com/huggingface/peft.git'
          --extra-index-url
          https://download.pytorch.org/whl/test/cu118
          'llama-recipes'
          'transformers>=4.31.0'
          sentencepiece
          py7zr
          scipy
          optimum
      env:
        - name: LD_LIBRARY_PATH
          value: /usr/local/nvidia/lib:/usr/local/nvidia/lib64:/opt/conda/lib
        - name: OCI_LOG_LEVEL
          value: DEBUG
        - name: HUGGING_FACE_HUB_TOKEN
          value: <your huggingface token>


```

Launch a distributed training job using following command - 

`ads opctl run -f llama2-ft-job.yaml`

Once the job is submitted, you should see there are 6 jobruns created under Job named - `LLAMA2-Fine-Tuning-lora-samsum-13b`


Check the progress of the training by running - 

`ads opctl watch <job run ocid of jobrun 0>`


# Testing finetuned weights and uploading the model to model catalog

1. Create a notebook session with VM.GPU.A10.2 shape or higher. Specify the object storage location where the finetuned weights are saved in the mount path while creating the notebook session.
2. Upload `lora-model-merge.ipynb` notebook to the notebook session
3. Run the notebook for verifying the fine tuned weights.
4. The notebook also has code to upload the fine tuned model to model catalog.

# Deployment

We will use vLLM based inference container for serving the fine tuned model.

vLLM offers various optimizations for efficient usage of GPU and offers good throughput out of the box.

We will use the model that was saved to model catalog after fine tuning job.

## Build Inference container - vLLM

Refer to [github samples](https://github.com/oracle-samples/oci-data-science-ai-samples/tree/main/model-deployment/containers/llama2) to build and publish the vllm based inference container

## Create model deployment

Prepare yaml file called `llama2-ft-md.yaml` from the template below. 

```
kind: deployment
spec:
  displayName: LLama2-13b model deployment
  infrastructure:
    kind: infrastructure
    type: datascienceModelDeployment
    spec:
      compartmentId: ocid1.compartment.oc1..xxxxxxxxxxxxx
      projectId: ocid1.datascienceproject.oc1.xxxx.xxxxxxxxxx
      accessLog:
        logGroupId: ocid1.loggroup.oc1.xxxx.xxxxxx
        logId: ocid1.log.oc1.xxxx.xxxx
      predictLog:
        logGroupId: ocid1.loggroup.oc1..xxxxxxxxxxxxx
        logId: ocid1.log.oc1.xxxx.xxxxxx
      shapeName: VM.GPU3.2
      replica: 1
      bandWidthMbps: 10
      webConcurrency: 1
      subnetId: ocid1.subnet.oc1.xxxx.xxxxxxxxxxx
  runtime:
    kind: runtime
    type: container
    spec:
      modelUri: ocid1.datasciencemodel.oc1.xxxx.xxxxxxxxxx
      image: {region}.ocir.io/{namespace}/{image-name}
      serverPort: 5001
      healthCheckPort: 5001
      env:
        PARAMS: "--model /opt/ds/model/deployed_model --tensor-parallel-size 2 --dtype half"
        TMPDIR: "/home/datascience"
      region: us-ashburn-1
      overwriteExistingArtifact: True
      removeExistingArtifact: True
      timeout: 100
      deploymentMode: HTTPS_ONLY

```

To start model deployment, run - 

`ads opctl run -f llama2-ft-md.yaml`

