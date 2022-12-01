# Oracle Data Science Service Jobs

This project contains samples that demonstrate usage of Oracle Data Science Service Jobs.

Oracle Data Science Service Jobs enables you to define and run a repeatable task on a fully managed infrastructure. Jobs is fully customizable and user-defined, you can apply any use case you may have such as data preparation, model training, hyperparameter tuning, batch inference, web scraping etc.

Using jobs, you can:

- Run Machine Learning or Data Science tasks outside of your notebooks (JupyterLab)
- Operationalize discrete data science and machine learning tasks as reusable executable operation
- Automate your typical MLOps or CI/CD Process
- Automate repeatable batches or workloads triggered by events or actions
- Batch Inference, Mini-Batch, Distributed Batch Jobs
- Distributed Training with Horovod, TensorFlow, PyTorch and Dask

Natively Jobs support Python and Shell scripts. If you utilize Bring Your Own Container feature with jobs, you can execute any language and environment you desire.

## Introduction

The repository contains set of folders for the programing languages we currently provide samples. Each folder contains codes of how to use the client OCI SDK, for example:

- `cli`, `node`,`python`,`shell`, `ts+js` the programing language client SDK samples
  
Depending on the programing language, like for example Python, we provide also sample Jobs in the sub folders.

- `sdk` showing how to use the OCI SDK Jobs API
- `job+samples` actual code samples you could run as a Job

## Samples

This repository provides following samples:

- `python` - OCI SDK samples with Jobs, as well as actual Job simple samples written in Python
- `shell` - simple shell scripts that can be executed as Jobs
- `ts+js` - client OCI SDK TypeScript and JavaScript samples of how to use to create and run Jobs
- `zip+tar` - provides ZIP or TAR packaged samples that can be run as Jobs
- `cli` - Oracle OCI CLI Client samples of how to create and run jobs
- `byoc` - Bring Your Own Container guide for Jobs
- `flask_job_monitoring` - a simple application to monitor multiple Job Run logs on your local machine
- `java` - Java client code implementing utilizing the Jobs Java OCI SDK
