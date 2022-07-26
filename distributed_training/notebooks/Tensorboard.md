# TensorBoard

TensorBoard helps visualizing your experiments. You bring up a ``TensorBoard`` session on your workstation and point to
the directory that contains the TensorBoard logs.

**Prerequisite**

1. Object storage bucket
2. Access to Object Storage bucket from your workstation
3. ``ocifs`` version 1.1.0 and above

Setting up local environment
----------------------------

It is required that ``tensorboard`` is installed in a dedicated conda environment or virtual environment. Prepare an
environment yaml file for creating conda environment with following command -

```
cat <<EOF > tensorboard-dep.yaml
dependencies:
- python=3.8
- pip
- pip:
    - ocifs
    - tensorboard
name: tensorboard
EOF
```

Create the conda environment from the yaml file generated in the preceeding step

    conda env create -f tensorboard-dep.yaml

This will create a conda environment called tensorboard. Activate the conda environment by running -

    conda activate tensorboard

**Using TensorBoard Logs:**

TensorBoard can be setup on a local machine and pointed to object storage. This will enable a live monitoring setup of
TensorBoard logs.

    OCIFS_IAM_TYPE=api_key tensorboard --logdir oci://<bucket_name>/path/to/logs

**Note**: The logs take some initial time (few minutes) to reflect on the tensorboard dashboard.

#### Writing TensorBoard logs to Object Storage

Your training script can write tensorboard logs to the directory reference by ``OCI__SYNC_DIR`` env variable.
With ``SYNC_ARTIFACTS=1`` in train.yaml, these TensorBoard logs will be periodically synchronized with the configured object storage
bucket. 

P.S. This 'sync' feature is only available in Horovod and dask at the moment. We're working on providing this for all the frameworks.

Training script modifications for using Tensorboard please refer: 
1. [Pytorch](https://github.com/pytorch/tutorials/blob/master/recipes_source/recipes/tensorboard_with_pytorch.py)
2. [Tensorflow](https://www.tensorflow.org/tensorboard/get_started)

