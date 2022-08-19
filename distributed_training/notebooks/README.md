# Distributed-training - Getting started

Here are the key pre-requisites that you would need to execute before you can proceed to building a
distributed workload docker image and execute it using odsc-jobs.

1. Configure Network. Required for the inter node communication.
2. OCI policies. Required for accessing oci services by the distributed job.   
3. Install ads-opctl. Required for packaging training script and launching odsc distributed job.

### 1. Networks

You need to use a private subnet for distributed training and config the ports in security list to allow traffic for communication between nodes. The following default ports are used by the corresponding frameworks:

* Dask:
    - Scheduler Port: 8786. More information [here](https://docs.dask.org/en/stable/deploying-cli.html#dask-scheduler)
    - Dashboard Port: 8787. More information [here](https://docs.dask.org/en/stable/deploying-cli.html#dask-scheduler)
    - Worker Ports: Default is Random. It is good to open a specific range of port and then provide the value in the startup option. More information [here](https://docs.dask.org/en/stable/deploying-cli.html#dask-worker)
    - Nanny Process Ports: Default is Random. It is good to open a specific range of port and then provide the value in the startup option. More information [here](https://docs.dask.org/en/stable/deploying-cli.html#dask-worker)

* PyTorch: By default, PyTorch uses 29400.
* Horovod: You need to allow all traffic within the subnet.

See also: [Security Lists](https://docs.oracle.com/en-us/iaas/Content/Network/Concepts/securitylists.htm)

### 2. OCI policies

Several OCI policies are needed for distributed training.

**Note** In the following example, ```group <your_data_science_users>``` is the subject of the policy. When starting the job from an OCI notebook session using resource principal, 
the subject should be ```dynamic-group```, for example, ```dynamic-group <your_notebook_sessions>```

Distributed training uses [OCI Container Registry](https://docs.oracle.com/en-us/iaas/Content/Registry/Concepts/registryoverview.htm) to store the container image.

To push images to container registry, the ```manage repos``` policy is needed, for example:
```
Allow group <your_data_science_users> to manage repos in compartment <your_compartment_name>
```

To pull images from container registry for local testing, the ```use repos``` policy is needed, for example:
```
Allow group <your_data_science_users> to read repos in compartment <your_compartment_name>
```

You can also restrict the permission to specific repository, for example:
```
Allow group <your_data_science_users> to read repos in compartment <your_compartment_name> where all { target.repo.name=<your_repo_name> }
```

See also: [Policies to Control Repository Access](https://docs.oracle.com/en-us/iaas/Content/Registry/Concepts/registrypolicyrepoaccess.htm)
To start distributed training jobs, the user will need access to multiple resources, including:

- ```read repos```
- ```manage data-science-jobs```
- ```manage data-science-job-runs```
- ```use virtual-network-family```
- ```manage log-groups```
- ```use log-content```
- ```read metrics```

For example:

```
Allow group <your_data_science_users> to manage data-science-jobs in compartment <your_compartment_name>
Allow group <your_data_science_users> to manage data-science-job-runs in compartment <your_compartment_name>
Allow group <your_data_science_users> to use virtual-network-family in compartment <your_compartment_name>
Allow group <your_data_science_users> to manage log-groups in compartment <your_compartment_name>
Allow group <your_data_science_users> to use logging-family in compartment <your_compartment_name>
Allow group <your_data_science_users> to use read metrics in compartment <your_compartment_name>
```

We also need policies for job runs, for example:

```
Allow dynamic-group <distributed_training_job_runs> to read repos in compartment <your_compartment_name>
Allow dynamic-group <distributed_training_job_runs> to use data-science-family in compartment <your_compartment_name>
Allow dynamic-group <distributed_training_job_runs> to use virtual-network-family in compartment <your_compartment_name>
Allow dynamic-group <distributed_training_job_runs> to use log-groups in compartment <your_compartment_name>
Allow dynamic-group <distributed_training_job_runs> to use logging-family in compartment <your_compartment_name>
```

See also [Data Science Policies](https://docs.oracle.com/en-us/iaas/data-science/using/policies.htm).

Distributed training uses OCI Object Storage to store artifacts and outputs. The bucket should be created before starting any distributed training. 
The ```manage objects``` policy is needed for users and job runs to read/write files in the bucket. 
The manage ```buckets policy``` is required for job runs to synchronize generated artifacts. For example:

```
Allow group <your_data_science_users> to manage objects in compartment your_compartment_name where all {target.bucket.name=<your_bucket_name>}
Allow dynamic-group <distributed_training_job_runs> to manage objects in compartment your_compartment_name where all {target.bucket.name=<your_bucket_name>}
Allow dynamic-group <distributed_training_job_runs> to manage buckets in compartment your_compartment_name where all {target.bucket.name=<your_bucket_name>}
```

See also [Object Storage Policies](https://docs.oracle.com/en-us/iaas/Content/Identity/Reference/objectstoragepolicyreference.htm#Details_for_Object_Storage_Archive_Storage_and_Data_Transfer)

### 3. Install ads-opctl and docker

Lastly, you need to install the ads-opctl utility which is required to package (dockerize) your distributed training script and
launch odsc distributed job.

* Install ADS >= 2.6.0

```
python3 -m pip install "oracle-ads[opctl]"
python3 -m pip install "oracle-ads[opctl]" --force-reinstall --no-deps --install-option="--enable-cli"
```

* Install docker. Refer https://docs.docker.com/get-docker

### Next steps 

Using the ads-opctl, download and initialize the relevant distributed training framework.

* Dask: 
  
  ```
  ads opctl distributed-training init --framework dask
  ```
* Horovod (Tensorflow):
  
  ```
  ads opctl distributed-training init --framework horovod-tensorflow --version v1
  ```
  
* Horovod (Pytorch):
  
  ```
  ads opctl distributed-training init --framework horovod-pytorch --version v1
  ```
  
* Pytorch Native: [pytorch.md](pytorch.md)
    ```
    ads opctl distributed-training init --framework pytorch --version v1
    ```

You are now all set to create, test locally and launch your distributed training workload. Refer these framework specific guides
to continue.

* Dask: [dask.md](dask.md)
* Horovod (Tensorflow and Pytorch): [horovod.md](horovod.md)
* Pytorch Native: [pytorch.md](pytorch.md)

