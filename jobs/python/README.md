# Python Job Samples

Oracle Data Science Service Jobs samples demonstrating how to use the OCI SDK Jobs API, as well as actual Python Jobs.

## Installation

If you want to try this samples on your local machine, we would recommend you to install and use Conda, as it allows for a good Python environment control

| :exclamation:  You would need Python 3.7+ to use the Python OCI SDK |
|-----------------------------------------|

### Using Conda

Download and install the Conda.

```bash
curl https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -o Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh
```

You may need to restart your terminal or source ~/.bashrc to enable the conda command. Use conda -V to test if it is installed successfully.

Create new conda environment with Python 3.7

```bash
conda create -n jobs python=3.8
```

Activate it.

```bash
conda deactivate
conda activate jobs
```

Install the OCI CLI Preview release

```bash
pip install oci
oci --version
```

## Setup

This samples use a **config.ini** to make the setup easier. In this config you can setup the OCIDs of your tenancy and use it with the SDK runner to run the Job directly against your tenancy.

## Run Samples

It is easy to run the samples with the provided `mljobs.py`.

Set your environment variables:

```bash
export PROJECT=<project ocid>
export COMPARTMENT=<compartment ocid>
export SUBNET=<subnet ocid>
export LOGGROUP=<log group ocid>
export TENANCY=<ini tenancy name>
export CONFIG=$HOME/.oci/config
```

- PROJECT: Data Science Service Project OCID
- COMPARTMENT: Data Science Service Project Compartment OCID
- SUBNET: VCN Private Subnet OCID to be used by the Job
- LOGGROUP: Log Group OCID to be used by the Job Runs to create the logs
- TENANCY: The name of the tenancy as set in the $HOME/.oci/config
- CONFIG: OCI API Key configuration location

Then run the `mljobs.py` and provide the file to be executed as a Job.

```bash
python mljobs.py -f ../samples/hello_world_job.py 
```
