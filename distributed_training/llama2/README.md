# Overview

In this tutorial you will learn how to run a multi-node multi-GPU distributed fine tuning of large language model and deploy the fine-tuned model using OCI Data Science service. We will use the Meta Llama2 [llama-recipe GitHub repo](https://github.com/facebookresearch/llama-recipes) for the distributed training code. 
You can select your preferred Llama2 model size in the setup configuration between the 7b or 13b parameters. The key objective of the fine tuning task is to summarize dialog/conversation.

## References

* [https://github.com/facebookresearch/llama-recipes](https://github.com/facebookresearch/llama-recipes)
* [https://accelerated-data-science.readthedocs.io/en/latest/user_guide/model_training/training_llm.html](https://accelerated-data-science.readthedocs.io/en/latest/user_guide/model_training/training_llm.html)
* [https://huggingface.co/datasets/samsum/viewer/samsum/test?row=11](https://huggingface.co/datasets/samsum/viewer/samsum/test?row=11)

## Prerequisite

The key prerequisites that you would need to set tup before you can proceed to run the distributed fine-tuning process on Oracle Cloud Infrastructure Data Science Service.

* [Configure custom subnet](https://github.com/oracle-samples/oci-data-science-ai-samples/tree/main/distributed_training#1-networking) - with security list to allow ingress into any port from the IPs originating within the CIDR block of the subnet. This is to ensure that the hosts on the subnet can connect to each other during distributed training.
* [Create an object storage bucket](https://github.com/oracle-samples/oci-data-science-ai-samples/tree/main/distributed_training#2-object-storage) - to save the fine tuned weights
* [Set the policies](https://github.com/oracle-samples/oci-data-science-ai-samples/tree/main/distributed_training#3-oci-policies) - to allow the OCI Data Science Service resources to access object storage buckets, networking and others
* [Access token from HuggingFace](https://huggingface.co/docs/hub/security-tokens) to download Llama2 model. To fine-tune the model, you will first need to access the pre-trained model. The pre-trained model can be obtained from [Meta](https://ai.meta.com/resources/models-and-libraries/llama-downloads/) or [HuggingFace](https://huggingface.co/models?sort=trending&search=meta-llama%2Fllama-2). In this example, we will use the [HuggingFace access token](https://huggingface.co/docs/hub/security-tokens) to download the pre-trained model from HuggingFace (by setting the __HUGGING_FACE_HUB_TOKEN__ environment variable).
* Log group and log from logging service. This will be used to monitor the progress of the training
  * Go to the [OCI Logging Service](https://cloud.oracle.com/logging/log-groups) and select `Log Groups`
  * Either select one of the existing Log Groups or create a new one
  * In the log group create ***two*** `Log`, one predict log and one access log, like:
    * Click on the `Create custom log`
    * Specify a name (predict|access) and select the log group you want to use
    * Under `Create agent configuration` select `Add configuration later`
    * Then click `Create agent configuration`
* [Notebook session](https://docs.oracle.com/en-us/iaas/data-science/using/manage-notebook-sessions.htm) - used to initiate the distributed training and to access the fine-tuned model
* Install the latest version of [oracle-ads](https://accelerated-data-science.readthedocs.io/en/latest/index.html) - `pip install oracle-ads[opctl] -U`

## Fine-Tuning The Llama2 Model

We will be using Oracle Cloud VM.GPU.A10.2 instances for this example. Generally it is recommend to expect as GPU memory required for the fine-tuning at least 4x times the size of the model in full precision. Our experiments show that the actual memory consumption ends up to be more, as you have to account for the memory consumption by the optimizer states, gradients, forward activations and more. For this example we've ended up using for the 7b models 4xA10's or 2xVM.GPU.A10.2 instances, and for the 13b we utilized 12xA10's which makes for 6xVM.GPU.A10.2. Hugging Face provides a [Model Memory Calculator](https://huggingface.co/spaces/hf-accelerate/model-memory-usage) and there is a great blog post about the topic from [Eleuther explaining the basic math behind the memory usage for transformers](https://blog.eleuther.ai/transformer-math/). Notice that single A10 GPU has 24GB of memory.

There are two ways to proceed with the fine-tuning, either by using the ADS Python APIs directly or create an YAML file with the required configuration and run it with the ADS OPCTL CLI. Let's start with the YAML approach first.

### YAML

Prepare a yaml file that describes the infrastructure and the job parameters. Use the template below and customize it with the resource IDs under infrastructure block. The shape name provided should be an instance with A10 or A100. Save the yaml file as `llama2-ft-job.yaml`

You can configure the number of nodes by changing the `replicas` attribute under `runtime` spec.

With 6 nodes and 13b parameter model, it will take about 2.5 hours to complete 3 epochs.

```yaml
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
        - name: OCI__METRICS_NAMESPACE
          value: finetune_llama2_13b
```

Replace the spec variables like `compartmentId`, `logGroupId`, `logId` etc. with the one from your Oracle Cloud Tenancy. Notice additionally the `outputUri` which should point to your object storage bucket where the fine-tuned model should be stored. Additionally you have to replace the `<your huggingface token>` with your token to access the Llama2 model from HuggingFace.

In this example, we have set up the `OCI__METRICS_NAMESPACE` to monitor closely the GPU utilization with the OCI Monitoring Service. The `replicas` specifies the number of instance that should be used, in this case `6xVM.GPU.A10.2` which would result in `12xA10` GPUs.

Notice, we used directly the [finetuning.py](https://github.com/facebookresearch/llama-recipes/blob/main/examples/finetuning.py) example as provided from the Meta Llama2 repository without additional configurations, all the Fine-Tuning Examples in the repository should work without modifications required.

To launch the distributed fine-tuning, open a Terminal in your OCI Data Science Notebook, install and activate a Conda environment with the latest Oracle ADS Library and then run the ADS OPCTL CLI:

```bash
odsc conda install -s pytorch20_p39_gpu_v2
activate /home/datascience/conda/pytorch20_p39_gpu_v2
ads opctl run -f llama2-ft-job.yaml
```

Once the job is submitted, you should see there are `6xJobRun's` created under Job named - `LLAMA2-Fine-Tuning-lora-samsum-13b`

Check the progress of the training by running in the Notebook Terminal:

```bash
ads opctl watch <job run ocid of job-run-ocid>
```

### ADS Python API

As we mention you could also run the fine-tuning process directly via the ADS Python API. Here the examples for fine-tuning full parameters of the [7B model](https://huggingface.co/meta-llama/Llama-2-7b-hf) using [FSDP](https://engineering.fb.com/2021/07/15/open-source/fsdp/).

```python
from ads.jobs import Job, DataScienceJob, PyTorchDistributedRuntime

job = (
    Job(name="LLAMA2-Fine-Tuning")
    .with_infrastructure(
        DataScienceJob()
        .with_log_group_id("<log_group_ocid>")
        .with_log_id("<log_ocid>")
        .with_compartment_id("<compartment_ocid>")
        .with_project_id("<project_ocid>")
        .with_subnet_id("<subnet_ocid>")
        .with_shape_name("VM.GPU.A10.1")
        .with_block_storage_size(256)
    )
    .with_runtime(
        PyTorchDistributedRuntime()
        # Specify the service conda environment by slug name.
        .with_service_conda("pytorch20_p39_gpu_v1")
        .with_git(
          url="https://github.com/facebookresearch/llama-recipes.git"
        )
        .with_dependency(
          pip_pkg=" ".join([
            "'accelerate>=0.21.0'",
            "appdirs",
            "loralib",
            "bitsandbytes==0.39.1",
            "black",
            "'black[jupyter]'",
            "datasets",
            "fire",
            "'git+https://github.com/huggingface/peft.git'",
            "'transformers>=4.31.0'",
            "sentencepiece",
            "py7zr",
            "scipy",
            "optimum"
          ])
        )
        .with_output("/home/datascience/outputs", "oci://bucket@namespace/outputs/")
        .with_command(" ".join([
          "torchrun llama_finetuning.py",
          "--enable_fsdp",
          "--pure_bf16",
          "--batch_size_training 1",
          "--micro_batch_size 1",
          "--model_name $MODEL_NAME",
          "--dist_checkpoint_root_folder /home/datascience/outputs",
          "--dist_checkpoint_folder fine-tuned"
        ]))
        .with_replica(2)
        .with_environment_variable(
          MODEL_NAME="meta-llama/Llama-2-7b-hf",
          HUGGING_FACE_HUB_TOKEN="<access_token>",
          LD_LIBRARY_PATH="/usr/local/nvidia/lib:/usr/local/nvidia/lib64:/opt/conda/lib",
        )
    )
)
```

## The Process

Regardless of whether you used the CLI or the Python API approach, the distributed job runs will:

* Setup the PyTorch conda environment and install additional dependencies.
* Fetch the source code from GitHub and checkout the specific commit.
* Run the training script with the specific arguments, which includes downloading the model and dataset.
* Save the outputs to OCI Object Storage once the training finishes.

Note that in the `torchrun` training command, there is no need to specify the number of nodes, the number of GPUs and the IP address of he main job. ADS will automatically configure those base on the `replica` and `shape` you specified, as shown on Figure 2 below.

![Oracle Cloud Infrastructure Data Science Distributed Jobs Process with ADS and PyTorch](images/jobs-distributed-training.002.png)

## Merging the fine-tuned weights and uploading the model to model catalog

After the fine-tuning process is complete, to test the new model, we have to merge the weights to the base model and upload to the OCI Data Science Model Catalog.

1. Create a notebook session with VM.GPU.A10.2 shape or higher. Specify the object storage location where the fine-tuned weights are saved in the mount path while creating the notebook session.
2. Upload `lora-model-merge.ipynb` notebook to the notebook session
3. Run the notebook for verifying the fine tuned weights.
4. The notebook also has code to upload the fine tuned model to model catalog.

## Deployment

We recommend to use vLLM based inference container for serving the fine-tuned model. vLLM offers various optimizations for efficient usage of GPU and offers good throughput out of the box. For the deployment, use the model that was saved to the model catalog after fine tuning job.

Refer to our [github llama2 deployment samples](https://github.com/oracle-samples/oci-data-science-ai-samples/tree/main/model-deployment/containers/llama2) to build and publish the vLLM based inference container and deploy the fine-tuned model.
