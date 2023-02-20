# Oracle Cloud Infrastructure Data Science Service - Distributed Training

## :book: Getting Started

Oracle Cloud Infrastructure Data Science Service supports distributed training with Jobs for the frameworks: Dask, Horovod, TensorFlow Distributed and PyTorch Distributed.

Here are the key pre-requisites that you would need to execute before you can proceed to run a distributed training on Oracle Cloud Infrastructure Data Science Service.

1. `Configure your network` - required for the inter node communication (P.S we are working to provide managed networking for your distributed cluster communication, coming soon)
2. `Create object storage bucket` - to be used for storing checkpoints, logs and other artifacts during the training process
3. `Set the policies` - required for accessing OCI services by the distributed job
4. `Configure your Auth Token` - to use the OCI SDK on your local machine, to create, run and monitor the jobs
5. `Install a desktop container management` - our cli requires dekstop container management tool to build, run and push your container images
6. `Install ads[opctl]` - required for packaging training script and launching OCI Data Science distributed jobs
7. `Create a container registry repository` - to store the container images that will be used during the distributed training

- `OCI` = [Oracle Cloud Infrastructure](https://docs.oracle.com/en-us/iaas/Content/home.htm)
- `DT` = [Distributed Training](../distributed_training/README.md)
- `ADS` = [Oracle Accelerated Data Science Library](https://docs.oracle.com/en-us/iaas/tools/ads-sdk/latest/index.html)
- `OCIR` = [Oracle Cloud Infrastructure Container Registry](https://docs.oracle.com/en-us/iaas/Content/Registry/home.htm#top)

## 1. Networking

You need to use a `private subnet` for distributed training and config the ports in the `VCN Security List` to allow traffic for communication between nodes. The following default ports are used by the corresponding frameworks:

**Note** we are working to provide managed networking for your distributed cluster communication, which will remove this configuration step in the future coming soon.

> &nbsp;
> **If you're working a Proof-of-Concept** you **can open all** the Ingress/Egress TCP ports in the subnet!
> &nbsp;

- Dask:
  - Scheduler Port: 8786. More information [here](https://docs.dask.org/en/stable/deploying-cli.html#dask-scheduler)
  - Dashboard Port: 8787. More information [here](https://docs.dask.org/en/stable/deploying-cli.html#dask-scheduler)
  - Worker Ports: Default is Random. It is good to open a specific range of port and then provide the value in the startup option. More information [here](https://docs.dask.org/en/stable/deploying-cli.html#dask-worker)
  - Nanny Process Ports: Default is Random. It is good to open a specific range of port and then provide the value in the startup option. More information [here](https://docs.dask.org/en/stable/deploying-cli.html#dask-worker)

- PyTorch: By default, PyTorch uses 29400.
- Horovod: You need to allow all traffic within the subnet.
- Tensorflow: Worker Port: Allow traffic from all source ports to one worker port (default: 12345). If changed, provide this in train.yaml config.

See also: [Security Lists](https://docs.oracle.com/en-us/iaas/Content/Network/Concepts/securitylists.htm)

### 2. Object Storage

> Create an object storage bucket at your Oracle Cloud Infrastructure to be used for the distibuted training.

Distributed training uses OCI Object Storage to store artifacts, outputs, checkpoints etc. The bucket should be created before starting any distributed training. The `manage objects` policy provided later in the guide is needed for users and job runs to read/write files in the bucket you will create and it is required for job runs to synchronize generated artifacts.

## 3. OCI Policies

To use Distributed Training on OCI Data Science Service, your accounts and services require access to multiple resources, which will be specified by the OCI Policies shown below.

### If You're Doing a Proof-of-Concept

If you're just trying out Oracle Cloud Infrastructure Data Science Distributed Training in a proof-of-concept project, you may not need more than a few administrators with full access to everything. In that case, you can simply create any new users you need and add them to the Administrators group. The users will be able to do anything with any kind of resource, and you can create all your resources directly in the tenancy (the root compartment). You don't need to create any compartments yet, or any other policies beyond the Tenant Admin Policy, which automatically comes with your tenancy and can't be changed. Additionally you have to create following resources:

1. Create a [Dynamic Group](https://docs.oracle.com/en-us/iaas/Content/Identity/Tasks/managingdynamicgroups.htm) in [your cloud tenancy](https://cloud.oracle.com/identity/dynamicgroups) with the following matching rules:
&nbsp;

    ```bash
    all { resource.type = 'datasciencenotebooksession' }
    all { resource.type = 'datasciencejobrun' }
    all { resource.type = 'datasciencemodeldeployment' }
    all { resource.type = 'datasciencepipelinerun' }
    ```

2. Create a [policy](https://docs.oracle.com/en-us/iaas/Content/Identity/Concepts/policies.htm) in [your root compartment](https://cloud.oracle.com/identity/policies) with the following statements:
&nbsp;

    ```xml
    allow service datascience to use virtual-network-family in tenancy
    allow dynamic-group <your-dynamic-group-name> to manage data-science-family in tenancy
    allow dynamic-group <your-dynamic-group-name> to manage all-resources in tenancy
    ```

    **Replace** `<your-dynamic-group-name>` with the name of your dynamic group!
    &nbsp;
3. Create new user(s) you need and add them to [your Administrators Group](https://cloud.oracle.com/identity/groups)

### If You're Past the Proof-of-Concept Phase

If you're past the proof-of-concept phase and want to restrict access to your resources, first:

- Make sure you're familiar with the basic IAM components, and read through the example scenario: [Overview of Identity and Access Management](https://docs.oracle.com/en-us/iaas/Content/Identity/Concepts/overview.htm#Overview_of_Oracle_Cloud_Infrastructure_Identity_and_Access_Management)
- Think about how to organize your resources into compartments: [Learn Best - Practices for Setting Up Your Tenancy](https://docs.oracle.com/en-us/iaas/Content/GSG/Concepts/settinguptenancy.htm#Setting_Up_Your_Tenancy)
- Learn the basics of how policies work: [How Policies Work](https://docs.oracle.com/en-us/iaas/Content/Identity/Concepts/policies.htm#How_Policies_Work)
- Check the [OCI Data Science Policies Guidance](https://docs.oracle.com/en-us/iaas/data-science/using/policies.htm)

At the high level the process is again as following:

1. Create a [Dynamic Group](https://docs.oracle.com/en-us/iaas/Content/Identity/Tasks/managingdynamicgroups.htm) in [your cloud tenancy](https://cloud.oracle.com/identity/dynamicgroups) with the following matching rules:
&nbsp;

    ```bash
    all { resource.type = 'datasciencenotebooksession' }
    all { resource.type = 'datasciencejobrun' }
    all { resource.type = 'datasciencemodeldeployment' }
    all { resource.type = 'datasciencepipelinerun' }
    ```

2. Create a [User Group](https://docs.oracle.com/en-us/iaas/Content/Identity/Tasks/managinggroups.htm) in [your cloud tenancy](https://cloud.oracle.com/identity/groups). Only the users beloging to this group would have access to the service, as per the policies we will write in the next step.
&nbsp;

3. Create the [policies](https://docs.oracle.com/en-us/iaas/Content/Identity/Concepts/policies.htm) in the compartment where you intend to use the OCI Data Science Service.
&nbsp;

    ```xml
    Allow service datascience to manage virtual-network-family in compartment <your_compartment_name>

    Allow dynamic-group <your-dynamic-group-name> to read repos in compartment <your_compartment_name>
    Allow dynamic-group <your-dynamic-group-name> to manage data-science-family in compartment <your_compartment_name>
    Allow dynamic-group <your-dynamic-group-name> to manage log-groups in compartment <your_compartment_name>
    Allow dynamic-group <your-dynamic-group-name> to manage log-content in compartment <your_compartment_name>
    Allow dynamic-group <your-dynamic-group-name> to manage objects in compartment <your_compartment_name>

    Allow group <your-data-science-users-group> to manage repos in compartment <your_compartment_name>
    Allow group <your-data-science-users-group> to manage data-science-family in compartment <your_compartment_name>
    Allow group <your-data-science-users-group> to use virtual-network-family in compartment <your_compartment_name>
    Allow group <your-data-science-users-group> to manage log-groups in compartment <your_compartment_name>
    Allow group <your-data-science-users-group> to manage log-content in compartment <your_compartment_name>
    Allow group <your-data-science-users-group> to read metrics in compartment <your_compartment_name>
    Allow group <your-data-science-users-group> to manage objects in compartment <your_compartment_name>
    ```

    **Replace** `<your-dynamic-group-name>`, `<your-data-science-users-group>` with your user group name and `<your_compartment_name>` with the name of the compartment where your distributed training should run.
    &nbsp;

4. Add the users required to have access to the Data Science service to the group you created in step (2) in [your tenancy](https://cloud.oracle.com/identity/groups)

#### Further Policy Restricting Access

You could restrict the permission to specific container repository, for example:

```xml
Allow <group|dynamic-group> <group-name> to read repos in compartment <your_compartment_name> where all { target.repo.name=<your_repo_name> }
```

See also: [Policies to Control Repository Access](https://docs.oracle.com/en-us/iaas/Content/Registry/Concepts/registrypolicyrepoaccess.htm)

Using following policy you could restrict acccess to a specific bucket only, for example:

```xml
Allow <group|dynamic-group> <group-name> to manage buckets in compartment <your_compartment_name> where all {target.bucket.name=<your_bucket_name>}
```

See also [Object Storage Policies](https://docs.oracle.com/en-us/iaas/Content/Identity/Reference/objectstoragepolicyreference.htm#Details_for_Object_Storage_Archive_Storage_and_Data_Transfer)

### 4. Configure Your Auth Token

Configure your [API Auth Token](https://docs.oracle.com/en-us/iaas/Content/Registry/Tasks/registrygettingauthtoken.htm) to be able to run and test your code locally and monitor the logs.

The OCI Auth Token is used for the OCI CLI and Python SDK. Follow the guidance from the online documentation to configure: <https://docs.oracle.com/en-us/iaas/Content/API/Concepts/apisigningkey.htm>

At the high level the instructions are:

- (1) login into your Oracle Cloud
- (2) select your account from the top right dropdown menu
- (3) generate a new API Auth Key
- (4) download the private key and store it into your `$HOME/.oci` folder
- (5) copy the suggested configuration and store it into your home directy `$HOME/.oci/config` file
- (6) change the `$HOME/.oci/config` with the suggested configuration in (5) and point to your private key
- (7) test the SDK or CLI

### 5. Install Desktop Container Management

ADS OPCTL CLI requires a container desktop tool to build, run, launch and push the containers. We support:

- [Docker Desktop](<https://docs.docker.com/get-docker>)
- [Rancher Desktop](<https://rancherdesktop.io/>)

### 6. Install ADS OPCTL CLI

Install the `ads[opctl]` CLI which is required to package (containerize) your distributed training script and launch OCI Data Science Distributed Training Jobs.

#### Setup Conda (optional, but recommended)

- For Linux and [Windows Subsystem for Linux](https://learn.microsoft.com/en-us/windows/wsl/about)

```bash
curl https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -o Miniconda3-latest-Linux-x86_64.sh
```

- MacOS Intel

```bash
curl https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-x86_64.sh -o Miniconda3-latest-MacOSX-x86_64.sh
```

- MacOS Apple Silicon

```bash
curl https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-arm64.sh -o Miniconda3-latest-MacOSX-arm64.sh
```

- Run the installer

Depending on your host system, get the one that much:

```bash
bash Miniconda3-latest-<Linux|MacOSX>-<x86_64|arm64>.sh
```

You may need to restart your terminal or run `source ~/.bashrc` or `~/.zshrc` to enable the conda command. Use `conda -V` to test if it is installed successfully.

- Create new conda

```bash
conda create -n distributed-training python=3.8
```

- Activate it

```bash
conda activate distributed-training
```

#### Install the CLI

- Install the `oracle-ads[opctl] >= 2.8.0` in the activated conda.

```bash
python3 -m pip install "oracle-ads[opctl]"
```

- Test the CLI is running

```bash
ads opctl -h
```

### 7. Login to Your OCIR

OCI Data Science Distributed Training uses [OCI Container Registry](https://docs.oracle.com/en-us/iaas/Content/Registry/Concepts/registryoverview.htm) to store the container image.

You may need to `docker login` to the Oracle Cloud Container Registry (OCIR) from your local machine, if you haven't done so before, to been able to push your images. To login you have to use your [API Auth Token](https://docs.oracle.com/en-us/iaas/Content/Registry/Tasks/registrygettingauthtoken.htm) that can be created under your `Oracle Cloud Account->Auth Token`. You need to login only once.

```bash
docker login -u '<tenant-namespace>/<username>' <region>.ocir.io
```

... where `<tenancy-namespace>` is the auto-generated Object Storage namespace string of your tenancy (as shown on the **Tenancy Information** page).

If your tenancy is **federated** with Oracle Identity Cloud Service, use the format `<tenancy-namespace>/oracleidentitycloudservice/<username>`

### 7. Create Container Registry Repository

Create a repository in your Container Registry in your Oracle Cloud, preferably in the same compartment where you will run the distributed training. For more information follow the [Creating a Repository Guide](https://docs.oracle.com/en-us/iaas/Content/Registry/Tasks/registrycreatingarepository.htm).

> Take a note of the `name` of the repository as well as the `namespace`, those will be used later.

### Next steps

You are now all set to create, test and launch your distributed training workload. Refer to the specific framework guides to continue.

- [Dask](dask.md)
- [Horovod (Tensorflow and Pytorch)](horovod.md)
- [PyTorch Native](pytorch.md)
- [Tensorflow Native](tensorflow.md)
- [Troubleshooting Guide](Troubleshooting.md)
