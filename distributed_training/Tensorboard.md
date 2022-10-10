# TensorBoard

TensorBoard helps visualizing your experiments. You bring up a ``TensorBoard`` session on your workstation and point to
the directory that contains the TensorBoard logs.

`OCI` = Oracle Cloud Infrastructure
`DT` = Distributed Training
`ADS` = Oracle Accelerated Data Science Library
`OCIR` = Oracle Cloud Infrastructure Registry

## Prerequisite

1. Object storage bucket
2. Access to Object Storage bucket from your workstation
3. `ocifs` version 1.1.0 and above

## Setting up local environment

It is required that ``tensorboard`` is installed in a dedicated conda environment or virtual environment. Prepare an
environment yaml file for creating conda environment with following command -

**tensorboard-dep.yaml**:

```yaml
dependencies:
    - python=3.8
    - pip
    - pip:
        - ocifs
        - tensorboard
name: tensorboard
```

Create the conda environment from the yaml file generated in the preceeding step

```bash
conda env create -f tensorboard-dep.yaml
```

This will create a conda environment called tensorboard. Activate the conda environment by running -

```bash
conda activate tensorboard
```

**Using TensorBoard Logs:**

To launch a TensorBoard session on your local workstation, run -

```bash
export OCIFS_IAM_KEY=api_key
tensorboard --logdir oci://my-bucket@my-namespace/path/to/logs
```

`OCIFS_IAM_KEY=api_key` - If you are using resource principal, set `resource_principal`

This will bring up TensorBoard app on your workstation. Access TensorBoard at ``http://localhost:6006/``

**Note**: The logs take some initial time (few minutes) to reflect on the tensorboard dashboard.

### Writing TensorBoard logs to Object Storage

Your training script can write tensorboard logs to the directory reference by ``OCI__SYNC_DIR`` env variable.

With ``SYNC_ARTIFACTS=1`` in train.yaml, these TensorBoard logs will be periodically synchronized with the configured object storage
bucket.

Training script modifications for using Tensorboard please refer:

1. [Pytorch](https://github.com/pytorch/tutorials/blob/master/recipes_source/recipes/tensorboard_with_pytorch.py)
2. [Tensorflow](https://www.tensorflow.org/tensorboard/get_started)

Also refer to the examples inside the [Horovod Readme](horovod.md)
