# Python Job Samples

Oracle Data Science Service Jobs samples demonstrating how to use the OCI SDK Jobs API, as well as actual Python Jobs. 
## Installation

If you want to try this samples on your local machine, we would recommend you to install and use Conda, as it allows for a good Python environment control

| :exclamation:  You would need Python 3.7+ to use the Python OCI SDK |
|-----------------------------------------|

### Using Conda

Download and install the Conda.

```bash
curl -L https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-x86_64.sh >> miniconda.sh
bash ./miniconda.sh -b -p $HOME/miniconda
cd $HOME/miniconda
./conda init <zsh or shell>
```

Create new conda environment with Python 3.7

```bash
conda create -n jobs python=3.7
```

Activate it.

```bash
conda activate jobs
```

Download the OCI CLI Preview release

```bash
pip install oci
oci --version
```
## Setup

This samples use a **config.ini** to make the setup easier. In this config you can setup the OCIDs of your tenancy and use it with the SDK runner to run the Job directly against your tenancy.

## Run Samples

It is easy to run the samples with the provided **mljobs.py**. To do so just pass which tenancy you want to use from your **config.ini** and the file you want to run as a job, for example:

```bash
python mljobs.py -t DEFAULT -f ../samples/hello_world_job.py 
```