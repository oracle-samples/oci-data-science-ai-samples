# Training GPT Model with PyTorch DDP

This tutorial shows how you can train GPT model with PyTorch distributed training on Oracle Cloud Infrastructure (OCI), including:
* Preparing container image with dependencies
* Defining distributed training job in YAML
* Running distributed training job with [Oracle Accelerated Data Science Library (ADS)](https://docs.oracle.com/en-us/iaas/tools/ads-sdk/latest/index.html)
* Loading training data from OCI [Object Storage](https://docs.oracle.com/iaas/Content/Object/Concepts/objectstorageoverview.htm)
* Saving checkpoints

This tutorial assumes you are familiar with:
* [PyTorch Distributed Data Parallel (DDP)](https://pytorch.org/tutorials/beginner/ddp_series_theory.html)
* [Multi-GPU Training](https://pytorch.org/tutorials/beginner/ddp_series_multigpu.html)
* [Multi-Node Training](https://pytorch.org/tutorials/intermediate/ddp_series_multinode.html)

Prerequisites:
* Configure your access to OCI. For more details about the configurations, see [Getting Started with Distributed Training on OCI](../distributed_training/README.md).
* Install Oracle ADS and enable CLI.
    ```
    python3 -m pip install "oracle-ads[opctl]"
    ```

## Introduction to minGPT

The official PyTorch tutorial "[Training “Real-World” Models With DDP](https://pytorch.org/tutorials/intermediate/ddp_series_minGPT.html)" used the [minGPT](https://github.com/karpathy/minGPT) model as an example to show some best practices when writing distributed training code. The minGPT model is a minimal PyTorch re-implementation of the [OpenAI GPT-2](https://github.com/openai/gpt-2).

In this tutorial, we will show how to run the training code provided in the [PyTorch examples](https://github.com/pytorch/examples/tree/main/distributed/minGPT-ddp). The following [video](https://www.youtube.com/watch?v=XFsFDGKZHh4) from PyTorch walks through the code.

[![Training GPT-like model with DDP](https://img.youtube.com/vi/XFsFDGKZHh4/0.jpg)](https://www.youtube.com/watch?v=XFsFDGKZHh4)

Following is another video from the author of minGPT explaining how to build a GPT model from scratch:

[![Training GPT-like model with DDP](https://img.youtube.com/vi/kCc8FmEb1nY/0.jpg)](https://www.youtube.com/watch?v=kCc8FmEb1nY)

## Preparing a Container Image

The artifacts required to build the container image are available at the **minGPT branch** of [this fork](https://github.com/qiuosier/pytorch_examples/tree/minGPT/distributed/minGPT-ddp/mingpt/oci_dist_training_artifacts) of the PyTorch examples.

To build the container image:
1. Clone the [repository](https://github.com/qiuosier/pytorch_examples.git)
    ```
    git clone https://github.com/qiuosier/pytorch_examples.git
    ```
2. Navigate into the repository and checkout the minGPT branch
    ```
    cd pytorch_examples
    git checkout minGPT
    ```
3. Navigate to `distributed/minGPT-ddp/mingpt`
    ```
    cd distributed/minGPT-ddp/mingpt
    ```
4. Set the `IMAGE_NAME` and `TAG` environment variables
    ```
    export IMAGE_NAME=<region.ocir.io/your-tenancy/your-image-name>
    export TAG=latest
    ```
5. Build the container image
    ```
    ads opctl distributed-training build-image -t $TAG -reg $IMAGE_NAME \
      -df oci_dist_training_artifacts/pytorch/v1_metrics/Dockerfile
    ```

## Defining Distributed Training Job in YAML

An template of the YAML defining the training job is available at `oci_dist_training_artifacts/pytorch_mingpt_fsdp.yaml`, and also [here](https://github.com/qiuosier/pytorch_examples/blob/minGPT/distributed/minGPT-ddp/mingpt/oci_dist_training_artifacts/pytorch_mingpt_fsdp.yaml). You will need to replace the `<>` values with your OCI configurations:
* In the `infrastucture.spec` section, configure the OCIDs.
* In the `cluster.spec` section, set the image value to the ones you used to build your image with format of `IMAGE_NAME:TAG`.
* In the `cluster.spec` section, set the `workDir` to an OCI object storage location with the format of `oci://bucket@namespace/prefix`.

To run the code from the official PyTorch examples, replace the `runtime` section with the following:
```
  runtime:
    apiVersion: v1.0
    kind: python
    type: "git"
    spec:
      uri: "https://github.com/pytorch/examples.git"
      branch: "main"
      entryPoint: "distributed/minGPT-ddp/mingpt/main.py"
      codeDir: "/home/datascience/pytorch"
```

Note that:
* The block storage will be mounted to `/home/datascience`. You should save your training code and data under this directory to untilize the block storage volume (specified in the infrastructure spec).
* The `VM.GPU.A10.1` GPU shape is specified in the `infrastucture.spec.shapeName`. Please select the shape based on your quota and limits.
* The number of main nodes (`cluster.spec.main.replica`) should always be `1`. By default, there will be one worker node (`cluster.spec.worker.replica`). You can update the number of nodes specified in `cluster.spec.worker.replica` as needed.

## Running Distributed Training Job

Since the training code requires GPU, you will not be able to test the code locally unless you have GPU available.

Run the following command to start the training job:
```
ads opctl run -f oci_dist_training_artifacts/pytorch_mingpt_fsdp.yaml | tee info.yaml
```

This command also saves the job run information to `info.yaml`, in which you can find the OCIDs of the job runs.

You can stream the logs using the following command with the OCID of the main job run:
```
ads opctl watch <MAIN_JOB_RUN_OCID>
```

Alternatively, you can run the [job monitor tool](https://github.com/oracle-samples/oci-data-science-ai-samples/tree/master/jobs/job_monitor) and monitor all your job runs in a web browser.

## Loading Data from OCI Object Storage

The [example code from PyTorch](https://github.com/pytorch/examples/blob/54f4572509891883a947411fd7239237dd2a39c3/distributed/minGPT-ddp/mingpt/char_dataset.py#L20) uses fsspec to read the [training data](https://raw.githubusercontent.com/karpathy/char-rnn/master/data/tinyshakespeare/input.txt), which can be specified as a argument for the training script. With Oracle ADS installed in the container image, you can also use object storage location without modifying the training code.

Assuming you have the training data at `oci://bucket@namespace/prefix/to/data`, you can use it with the following `runtime` spec:

```
  runtime:
    apiVersion: v1.0
    kind: python
    type: "git"
    spec:
      uri: "https://github.com/pytorch/examples.git"
      branch: "main"
      entryPoint: "distributed/minGPT-ddp/mingpt/main.py"
      codeDir: "/home/datascience/pytorch"
      args:
        - data_config.path=oci://bucket@namespace/prefix/to/data
```

You can find all the supported arguments in [gpt2_train_cfg.yaml](https://github.com/pytorch/examples/blob/main/distributed/minGPT-ddp/mingpt/gpt2_train_cfg.yaml).

Please keep in mind that the I/O performance is limited when using fsspec to access remote files. When you have large dataset, it is better to copy the data into the job run before start the training.

## Saving Checkpoints

The [example code from PyTorch](https://github.com/pytorch/examples/blob/54f4572509891883a947411fd7239237dd2a39c3/distributed/minGPT-ddp/mingpt/trainer.py#L134) contains code to save snapshots (checkpoints) to S3 bucket. We can update the `_save_snapshot()` method with `fsspec` so that the checkpoints can be saved to OCI object storage as well.

```
def _save_snapshot(self, epoch):
    # capture snapshot
    model = self.model
    raw_model = model.module if hasattr(model, "module") else model
    snapshot = Snapshot(
        model_state=raw_model.state_dict(),
        optimizer_state=self.optimizer.state_dict(),
        finished_epoch=epoch
    )
    # save snapshot
    snapshot = asdict(snapshot)

    with fsspec.open(self.config.snapshot_path, 'w') as fp:
        torch.save(snapshot, fp)

    print(f"Snapshot saved at epoch {epoch}")
```

You will also need to specify the snapshot location using the arguments:
```
  runtime:
    apiVersion: v1.0
    kind: python
    type: "git"
    spec:
      uri: "https://github.com/pytorch/examples.git"
      branch: "main"
      entryPoint: "distributed/minGPT-ddp/mingpt/main.py"
      codeDir: "/home/datascience/pytorch"
      args:
        - data_config.path=oci://bucket@namespace/prefix/to/data
        - trainer_config.snapshot_path=oci://bucket@namespace/prefix/to/snapshot.pt
```
