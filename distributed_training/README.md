# Distributed Training - Getting Started

Here are the key pre-requisites that you would need to execute before you can proceed to building a distributed workload docker image and execute it using odsc-jobs.

1. `Configure Your Network` - required for the inter node communication (P.S we are working to provide managed networking for your distributed cluster communication, coming soon)
2. `Create object storage bucket` - to be used for storing checkpoints, logs and other artifacts during the training process
3. `Set OCI policies` - required for accessing OCI services by the distributed job
4. `Install ads-opctl` - required for packaging training script and launching OCI Data Science distributed jobs

`OCI` = Oracle Cloud Infrastructure
`DT` = Distributed Training
`ADS` = Oracle Accelerated Data Science Library
`OCIR` = Oracle Cloud Infrastructure Registry

## 1. Networks

You need to use a `private subnet` for distributed training and config the ports in the `VCN Security List` to allow traffic for communication between nodes. The following default ports are used by the corresponding frameworks:

**Note** we are working to provide managed networking for your distributed cluster communication, which will remove this configuration step in the future coming soon.

* Dask:
  * Scheduler Port: 8786. More information [here](https://docs.dask.org/en/stable/deploying-cli.html#dask-scheduler)
  * Dashboard Port: 8787. More information [here](https://docs.dask.org/en/stable/deploying-cli.html#dask-scheduler)
  * Worker Ports: Default is Random. It is good to open a specific range of port and then provide the value in the startup option. More information [here](https://docs.dask.org/en/stable/deploying-cli.html#dask-worker)
  * Nanny Process Ports: Default is Random. It is good to open a specific range of port and then provide the value in the startup option. More information [here](https://docs.dask.org/en/stable/deploying-cli.html#dask-worker)

* PyTorch: By default, PyTorch uses 29400.
* Horovod: You need to allow all traffic within the subnet.
* Tensorflow: Worker Port: Allow traffic from all source ports to one worker port (default: 12345). If changed, provide this in train.yaml config.

See also: [Security Lists](https://docs.oracle.com/en-us/iaas/Content/Network/Concepts/securitylists.htm)

### 2. Object Storage

Create an object storage bucket at your Oracle Cloud Infrastructure to be used for the distibuted training.

Distributed training uses OCI Object Storage to store artifacts and outputs. The bucket should be created before starting any distributed training. The ```manage objects``` policy provided later in the guide is needed for users and job runs to read/write files in the bucket you will create. The manage ```buckets policy``` is required for job runs to synchronize generated artifacts. Point those policies to the bucket you created for the distributed training.

## 3. OCI Policies

To start distributed training jobs on OCI Data Science Service, the user will need access to multiple resources, which will be specified by the OCI Policies shown below.

Note that distributed training uses [OCI Container Registry](https://docs.oracle.com/en-us/iaas/Content/Registry/Concepts/registryoverview.htm) to store the container image.

### User Group Policies

* ```manage repos```
* ```manage data-science-family```
* ```use virtual-network-family```
* ```manage log-groups```
* ```manage log-content```
* ```to manage objects```
* ```read metrics```

**_Example_**:

```xml
Allow group <your_data_science_users-group> to manage repos in compartment <your_compartment_name>
Allow group <your_data_science_users-group> to manage data-science-family in compartment <your_compartment_name>
Allow group <your_data_science_users-group> to use virtual-network-family in compartment <your_compartment_name>
Allow group <your_data_science_users-group> to manage log-groups in compartment <your_compartment_name>
Allow group <your_data_science_users-group> to manage log-content in compartment <your_compartment_name>
Allow group <your_data_science_users-group> to read metrics in compartment <your_compartment_name>
Allow group <your_data_science_users-group> to manage objects in compartment <your_compartment_name> where all {target.bucket.name=<your_bucket_name>}
```

**Note** In the example, ```group <your_data_science_users-group>``` is the subject of the policy. When starting the job from an OCI Data Science Notebook Session using resource principal, the subject should be ```dynamic-group```, for example, ```dynamic-group <your_notebook_sessions>```, for more see the Dynamic Group Policies

### Dynamic Group Policies

* ```read repos```
* ```manage data-science-family```
* ```use virtual-network-family```
* ```manage log-groups```
* ```manage log-content```
* ```to manage objects```
* ```read metrics```

**_Example_**:

```xml
Allow dynamic-group <your-dynamic-group-name> to read repos in compartment <your_compartment_name>
Allow dynamic-group <your-dynamic-group-name> to manage data-science-family in compartment <your_compartment_name>
Allow dynamic-group <your-dynamic-group-name> to manage log-groups in compartment <your_compartment_name>
Allow dynamic-group <your-dynamic-group-name> to manage log-content in compartment <your_compartment_name>
Allow dynamic-group <your-dynamic-group-name> to manage objects in compartment your_compartment_name where all {target.bucket.name=<your_bucket_name>}
Allow service datascience to manage virtual-network-family in compartment <your_compartment_name>
```

See also [Data Science Policies](https://docs.oracle.com/en-us/iaas/data-science/using/policies.htm).

**_Example for an OCI Data Science Service Dynamic Group Rules_**:

```bash
all {resource.type='datasciencejobrun',resource.compartment.id='ocid1.compartment.oc1..aaaaaaaa<>'}
all {resource.type='datasciencemodeldeployment',resource.compartment.id='ocid1.compartment.oc1..aaaaaaaa<>'}
all {resource.type='datasciencenotebooksession',resource.compartment.id='ocid1.compartment.oc1..aaaaaaaa<>'}
```

**Note** `resource.compartment.id` point to the OCID of your compartment

### Further Restricting Access

You can restrict the permission to specific container repository, for example:

```xml
Allow <group|dynamic-group> <group-name> to read repos in compartment <your_compartment_name> where all { target.repo.name=<your_repo_name> }
```

See also: [Policies to Control Repository Access](https://docs.oracle.com/en-us/iaas/Content/Registry/Concepts/registrypolicyrepoaccess.htm)

Using following policy you could restrict acccess to a specific bucket only, for example:

```xml
Allow <group|dynamic-group> <group-name> to manage buckets in compartment <your_compartment_name> where all {target.bucket.name=<your_bucket_name>}
```

See also [Object Storage Policies](https://docs.oracle.com/en-us/iaas/Content/Identity/Reference/objectstoragepolicyreference.htm#Details_for_Object_Storage_Archive_Storage_and_Data_Transfer)

### 4. Install ads opctl and container management

Lastly, you need to install the ads-opctl utility which is required to package (containerize) your distributed training script and
launch OCI Data Science distributed jobs.

* Setup Conda (optional, but recommended)

```bash
curl https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -o Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh
conda create -n distributed-training python=3.8
conda activate distributed-training
```

* Install ADS >= 2.6.6

```bash
python3 -m pip install "oracle-ads[opctl]"
```

* Install Docker. Refer <https://docs.docker.com/get-docker>
**Note** A good alternative solution to Docker for your local environment is Rancher Desktop <https://rancherdesktop.io/>

### Next steps

Using the `ads opctl`, download and initialize the relevant distributed training framework in your project folder.

* Dask:
  
  ```bash
  ads opctl distributed-training init --framework dask
  ```

* Horovod (Tensorflow):
  
  ```bash
  ads opctl distributed-training init --framework horovod-tensorflow --version v1
  ```
  
* Horovod (Pytorch):
  
  ```bash
  ads opctl distributed-training init --framework horovod-pytorch --version v1
  ```
  
* Pytorch Native: [pytorch.md](pytorch.md)

    ```bash
    ads opctl distributed-training init --framework pytorch --version v1
    ```

* Tensorflow Native: [tensorflow.md](tensorflow.md)

    ```bash
    ads opctl distributed-training init --framework tensorflow --version v1
    ```

You are now all set to create, test locally and launch your distributed training workload. Refer these framework specific guides
to continue.

* Dask: [dask.md](dask.md)
* Horovod (Tensorflow and Pytorch): [horovod.md](horovod.md)
* Pytorch Native: [pytorch.md](pytorch.md)
* Tensorflow Native: [tensorflow.md](tensorflow.md)
