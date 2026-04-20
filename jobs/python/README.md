# Python Job Samples

Oracle Data Science Service Jobs samples demonstrating how to use the OCI SDK Jobs API, and Python based Jobs code samples.

## Installation

If you want to try this samples on your local machine, we would recommend you to install and use Conda, as it allows for a good Python environment control.

> Python 3.8+ is required to run the samples in this guide.

### Using Conda

Install Miniforge, a conda-forge-based Conda distribution, by following the Miniforge installation guide: <https://github.com/conda-forge/miniforge#install>

- For Linux and [Windows Subsystem for Linux](https://learn.microsoft.com/en-us/windows/wsl/about)

```bash
curl -L https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh -o Miniforge3-Linux-x86_64.sh
```

- MacOS Intel

```bash
curl -L https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-MacOSX-x86_64.sh -o Miniforge3-MacOSX-x86_64.sh
```

- MacOS Apple Silicon

```bash
curl -L https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-MacOSX-arm64.sh -o Miniforge3-MacOSX-arm64.sh
```

Run the installer

```bash
bash Miniforge3-<Linux|MacOSX>-<x86_64|arm64>.sh
```

> You may need to restart your terminal or `source ~/.bashrc` or `~/.zshrc` to enable the conda command. Use `conda -V` to test if it is installed successfully.

Create new conda environment with Python 3.8

```bash
conda create -n jobs python=3.8
```

Activate it.

```bash
conda activate jobs
```

Install the OCI CLI Python SDK

```bash
pip install oci
oci --version
```

## Run the Samples

It is easy to run the samples with the `/sdk/mljobs.py`

Set your environment variables in your terminal:

```bash
export PROJECT=<project ocid>
export COMPARTMENT=<compartment ocid>
export SUBNET=<subnet ocid>
export LOGGROUP=<log group ocid>
export TENANCY=<oci config profile>
export CONFIG=$HOME/.oci/config
```

- `PROJECT`: Data Science Service Project OCID
- `COMPARTMENT`: Data Science Service Project Compartment OCID
- `SUBNET`: VCN Private Subnet OCID to be used by the Jobs
- `LOGGROUP`: Log Group OCID to be used by the Job Runs to create the logs
- `TENANCY`: The `profile name` as set in your `~/.oci/config` file, default name is usually `DEFAULT`
- `CONFIG`: OCI API Key configuration file location, default `$HOME/.oci/config`

Use the `/sdk/jobs-runner.py` and set the file to be ran as a Job.

Example:

```bash
python jobs-runner.py -f ../job+samples/hello_world_job.py 
```
