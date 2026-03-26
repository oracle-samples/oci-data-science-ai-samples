# Active Service Conda Environments for OCI Data Science

This page is the customer-facing source of truth for the **currently active service conda environments** available for OCI Data Science workflows.

Deprecated environments are not listed here. When multiple active revisions exist for the same environment family, this page shows only the latest active version for that Python version and platform.

## What service conda environments are

Service conda environments are curated environments provided for OCI Data Science. Each one packages a tested set of Python, libraries, and OCI integrations for a specific type of work, such as general machine learning, Spark, forecasting, or GPU-based deep learning.

They give you a ready-to-use starting point so you do not need to assemble and validate every dependency yourself.

## Why customers use them

Service conda environments matter because they help you:

- start faster with a known-good environment,
- choose an environment aligned to a common workflow,
- keep notebook-based work consistent across teams, and
- avoid unnecessary package and dependency setup work.

## Notebook sessions and Environment Explorer

These environments are used most often in **notebook sessions**, which open in JupyterLab.

In OCI Data Science notebook sessions, you can use **Environment Explorer** to:

- view available service conda environments,
- install an environment into your notebook session, and
- use the installed environment as a notebook kernel for your work.

For most customers, this is the easiest way to discover, install, and start using a service conda environment.

## Scope of this page

This page is intentionally not a historical inventory of every conda environment ever published.

It is a concise reference for the **active environments customers should see as available today**, based on the current production-published inventory and the corresponding environment manifests in this repository.

## Active environments

### Base environments

| Environment | Slug | Primary use case | Description |
|---|---|---|---|
| Python 3.10 Base environment | `python_p310_any_x86_64_v2` | Start from a minimal Python environment and add your own packages | Base Python 3.10 environment for customization. |
| Python 3.11 Base environment | `python_p311_any_x86_64_v3` | Start from a minimal Python environment and add your own packages | Base Python 3.11 environment for customization. |
| Python 3.12 Base environment | `python_p312_any_x86_64_v2` | Start from a minimal Python environment and add your own packages | Base Python 3.12 environment for customization. |

### General-purpose machine learning

| Environment | Slug | Primary use case | Description |
|---|---|---|---|
| General Machine Learning for CPUs on Python 3.11 | `generalml_p311_cpu_x86_64_v3` | Broad CPU-based machine learning and data science workflows | General-purpose machine learning environment with Oracle data-access libraries plus core ML packages such as scikit-learn, XGBoost, and LightGBM. |
| General Machine Learning for CPUs on Python 3.12 | `generalml_p312_cpu_x86_64_v1` | Broad CPU-based machine learning and data science workflows | General-purpose machine learning environment on Python 3.12 with Oracle integrations and common ML libraries for tabular and classical ML work. |

### GPU deep learning and inference

| Environment | Slug | Primary use case | Description |
|---|---|---|---|
| PyTorch 2.8 for GPU on Python 3.12 | `pytorch28_p312_gpu_x86_64_v1` | PyTorch-based model training, fine-tuning, and modern deep learning workflows | GPU environment for PyTorch workloads, including CUDA support and commonly used libraries for transformer and LLM-oriented development. |
| TensorFlow 2.20 for GPU on Python 3.12 | `tensorflow220_p312_gpu_x86_64_v1` | TensorFlow training and inference on GPU | GPU environment for TensorFlow-based deep learning workflows, including TensorFlow, TensorBoard, and core data science packages. |
| ONNX Runtime on Python 3.12 with GPU support | `onnxruntime_p312_gpu_x86_64_v1` | GPU-backed ONNX inference workloads | Environment focused on ONNX model inference, including GPU-enabled ONNX Runtime and support for inference scenarios such as embeddings and text generation. |

### Spark and Data Flow

| Environment | Slug | Primary use case | Description |
|---|---|---|---|
| PySpark 3.5 and Data Flow on Python 3.11 | `pyspark35_p311_cpu_x86_64_v1` | Spark, Data Flow, and large-scale data processing workflows | PySpark environment with Data Flow magic commands for working with remote Data Flow sessions from notebook sessions. |
| PySpark 3.5 and Data Flow on Python 3.12 | `pyspark35_p312_cpu_x86_64_v1` | Spark, Data Flow, and large-scale data processing workflows | PySpark environment on Python 3.12 with Data Flow integration for notebook-based Spark and distributed data processing. |

### Operator-focused environments

| Environment | Slug | Primary use case | Description |
|---|---|---|---|
| AI Forecasting Operator | `forecast_p311_cpu_x86_64_v13` | Time-series forecasting workflows with Oracle ADS operator support | Environment focused on forecasting workflows, including Oracle ADS, AutoMLX, and forecasting libraries such as Prophet, NeuralProphet, AutoTS, and pmdARIMA. |

### ARM environments

| Environment | Slug | Primary use case | Description |
|---|---|---|---|
| ARM Pack for Machine Learning on Python 3.12 | `armml_p312_cpu_aarch64_v1` | Machine learning workflows on ARM-based notebook, job, pipeline, and deployment shapes | ARM-targeted machine learning environment for data access, classical ML, and ONNX-related workflows on ARM infrastructure. |

## How to choose an environment

- Choose a **Base environment** if you want the lightest starting point and plan to install most of your own dependencies.
- Choose **General Machine Learning** if you want a broad default environment for CPU-based data science and machine learning work.
- Choose **PyTorch**, **TensorFlow**, or **ONNX Runtime** when your workflow is tied to one of those frameworks and you want a GPU-ready setup.
- Choose **PySpark and Data Flow** if your work depends on Spark sessions, distributed processing, or OCI Data Flow integration.
- Choose **AI Forecasting Operator** if your workflow is centered on time-series forecasting with the Oracle ADS operator stack.
- Choose **ARM Pack for Machine Learning** only when you are working on ARM-based infrastructure.