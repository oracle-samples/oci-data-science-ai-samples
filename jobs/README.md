# Oracle Data Science Service Jobs

- `OCI` = [Oracle Cloud Infrastructure](https://docs.oracle.com/en-us/iaas/Content/home.htm)
- `DT` = [Distributed Training](../distributed_training/README.md)
- `ADS` = [Oracle Accelerated Data Science Library](https://docs.oracle.com/en-us/iaas/tools/ads-sdk/latest/index.html)
- `OCIR` = [Oracle Cloud Infrastructure Container Registry](https://docs.oracle.com/en-us/iaas/Content/Registry/home.htm#top)

This project consist of examples that demonstrate usage of Oracle Cloud Infrastructure Data Science Jobs.

Oracle Cloud Data Science Service Jobs enables you to define and run a repeatable task on a fully managed infrastructure. Jobs is fully customizable and user-defined, you can apply any use case you may have such as data preparation, model training, hyperparameter tuning, batch inference, web scraping etc.

Using jobs, you can:

- Run machine learning or data science tasks outside of your notebooks (JupyterLab)
- Operationalize discrete data science and machine learning tasks as reusable executable operation
- Automate your typical MLOps or CI/CD Process
- Automate repeatable batches or workloads triggered by events or actions
- Process your batch inference, mini-batch and distributed batch jobs
- Run [distributed training](../distributed_training/README.md) with Horovod, TensorFlow, PyTorch and Dask

Natively Jobs support Python and Shell scripts, but you could also Bring Your Own Container with jobs, which enables you to execute any language and environment you desire.

## Introduction

The repository contains set of folders for the programing languages we currently provide samples. Each folder contains codes of how to use the client OCI SDK, for example:

- `cli`, `node`,`python`,`shell`, `ts+js` the programing language client SDK samples
  
Depending on the programing language, like for example Python, we provide also sample Jobs in the sub folders.

- `sdk` Oracle Cloud SDK Jobs API implementation samples
- `job+samples` actual code samples you could run as a Job

## Samples

This repository provides following samples:

- `byoc` - Bring Your Own Container guide and sample
- `cli` - Oracle OCI CLI client samples of how to create and run jobs
- `flask_job_monitoring` - a simple application to monitor multiple Job Run logs on your local or compute machine
- `java` - Java client code implementing utilizing the Oracle Cloud Jobs Java OCI SDK
- `python` - OCI SDK API sample, as well as actual Job simple samples written in Python
- `shell` - shell scripts example that can be executed as a Job
- `ts+js` - client OCI SDK TypeScript and JavaScript samples of how to use to create and run Job
- `zip+tar` - provides ZIP or TAR packaged samples that can be run as a Job

## Getting Started

The key pre-requisites that you would need before you can proceed to use OCI Data Science Jobs.

### If You're Doing a Proof-of-Concept

If you're just trying out Oracle Cloud Infrastructure Data Science or doing a proof-of-concept project, you may not need more than a few administrators with full access to everything. In that case, you can simply create any new users you need and add them to the Administrators group. The users will be able to do anything with any kind of resource, and you can create all your resources directly in the tenancy (the root compartment). You don't need to create any compartments yet, or any other policies beyond the Tenant Admin Policy, which automatically comes with your tenancy and can't be changed. Additionally you have to create following resources:

1. Create a [Dynamic Group](https://docs.oracle.com/en-us/iaas/Content/Identity/Tasks/managingdynamicgroups.htm) in [your cloud tenancy](https://cloud.oracle.com/identity/dynamicgroups) with the following matching rules:
&nbsp;

    ```bash
    all { resource.type = 'datasciencenotebooksession' }
    all { resource.type = 'datasciencejobrun' }
    all { resource.type = 'datasciencemodeldeployment' }
    ```

2. Create a [policy](https://docs.oracle.com/en-us/iaas/Content/Identity/Concepts/policies.htm) in [your root compartment](https://cloud.oracle.com/identity/policies) with the following statements:
&nbsp;

    ```xml
    allow service datascience to use virtual-network-family in tenancy
    allow dynamic-group <your-dynamic-group-name> to manage data-science-family in tenancy
    allow dynamic-group <your-dynamic-group-name> to manage all-resources in tenancy
    ```

    &nbsp;
    **Replace** `<your-dynamic-group-name>` with the name of your dynamic group!
    &nbsp;
3. If you create new users add them to your [Administrators Group](https://cloud.oracle.com/identity/groups)

### If You're Past the Proof-of-Concept Phase

If you're past the proof-of-concept phase and want to restrict access to your resources, first:

- Make sure you're familiar with the basic IAM components, and read through the example scenario: [Overview of Identity and Access Management](https://docs.oracle.com/en-us/iaas/Content/Identity/Concepts/overview.htm#Overview_of_Oracle_Cloud_Infrastructure_Identity_and_Access_Management)
- Think about how to organize your resources into compartments: [Learn Best - Practices for Setting Up Your Tenancy](https://docs.oracle.com/en-us/iaas/Content/GSG/Concepts/settinguptenancy.htm#Setting_Up_Your_Tenancy)
- Learn the basics of how policies work: [How Policies Work](https://docs.oracle.com/en-us/iaas/Content/Identity/Concepts/policies.htm#How_Policies_Work)
- Check the [OCI Data Science Policies Guidance](https://docs.oracle.com/en-us/iaas/data-science/using/policies.htm)
- Provision your policies with the [Oracle Resource Manager Template for Data Science](https://docs.oracle.com/en-us/iaas/data-science/using/orm-configure-tenancy.htm)

## Your First Job

Let's create simple hello world job and run it on Oracle Cloud Infrastructure Data Science Jobs Service.

### Step 1 - prepare sample code

Create a file called [hello_world_job.py](python/job%2Bsamples/hello_world_job.py)

```bash
import time

print("Hello world!")
time.sleep(3)
print("Job Done.")
```

### Step 2 - create a job

Login with your Oracle Cloud account then:

- go to the Data Science Service
- click on the button `Create Project` and create a new project
- select the new project
- under `Resources` go to `Jobs`
- click on the `Create job` button
- under `Upload job artifact` click on `select a file` link and select the file `hello_world_job.py` on your computer
- in the `Logging` section click on the `Select` button, make sure that `Enable logging` is selected and choose your `Log group` from the Drop-Down (if no Log Group appears, you have to create one!)
- make sure that the option `Enable automatic log creation` is selected and click on `Select` button
- set the `Storage` to be at least 50GB
- leave the `Default Networking` configuration
- click on `Create` to create the job

### Step 3 - run the job

- in the Oracle Cloud console under the `Jobs` resource select the job that you created in the previous step
- click on the `Start a job run` button to start the job
- there is no need to override the job configuration, leave everything as-is
- click on the `Start` button

The job will automatically provison and execute your code. You can click on the Job Run that will be created and monitor the progress. Under the `Logging details` of the Job Run a `Log` will be created, you can click on the link to view the prints from your code in the OCI Logging Service.
