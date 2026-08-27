# Active Service Conda Environments for OCI Data Science

This page lists the current service conda environment revisions in the OL9 migration inventory. Deprecated environments are not included.

During the Oracle Linux 9 migration, both an Oracle Linux 8 (OL8)-built revision and an Oracle Linux 9 (OL9)-built revision can be active for the same environment family. When both are active, the tables below show the latest active revision for each build base.

> **Regional availability:** Catalog publication is rolled out by region and realm. A revision in the migration inventory is not a guarantee that it has reached every production region. Use Environment Explorer in your OCI Data Science notebook session to confirm which revisions are available in your region.

## What service conda environments are

Service conda environments are curated environments provided for OCI Data Science. Each one packages a tested set of Python, libraries, and OCI integrations for a specific type of work, such as general machine learning, Spark, forecasting, or GPU-based deep learning.

They give you a ready-to-use starting point so you do not need to assemble and validate every dependency yourself.

## Why customers use them

Service conda environments help you:

- start faster with a curated environment,
- choose an environment aligned to a common workflow,
- keep notebook-based work consistent across teams, and
- reduce package and dependency setup work.

## Notebook sessions and Environment Explorer

These environments are used most often in **notebook sessions**, which open in JupyterLab. In Environment Explorer, you can:

- view the service conda environments available in your region,
- install an environment into your notebook session, and
- use the installed environment as a notebook kernel.

For most customers, this is the easiest way to discover, install, and start using a service conda environment.

## Oracle Linux build base

For the migration pairs on this page, the **Build base** column identifies the Oracle Linux container used to build the SCE. It is separate from the environment's Python version, processor architecture, and CPU or GPU type. It does not change the runtime image beneath your workload, and it does not mean that the SCE can run only with the same runtime-image version.

The latest active OL8-built migration revisions listed here are generally intended to run with both OL8 and OL9 runtime images. Review documented exceptions, including the PySpark Jobs issue below. This supports a staged migration: you can move an existing workload to an OL9 runtime image while continuing to use its OL8-built SCE, and then migrate the SCE separately.

> **Required for PySpark 3.5 Jobs:** Jobs that use `pyspark35_p312_cpu_x86_64_v1` must move to `pyspark35_p312_cpu_x86_64_v2` before running on the OL9 Jobs runtime image. The OL8-built `v1` revision failed OL9 Jobs validation because of a GDAL compatibility issue. The OL9-built `v2` revision passed Jobs, Model Deployment, and Notebook validation.

OL9-built revisions target the OL9 runtime image and may depend on newer system libraries, such as a newer GLIBC version, so they are not intended for the OL8 runtime image. For new workloads on OL9, prefer the corresponding **OL9-built** revision. Existing workloads can continue using the OL8-built revision while migrating and testing. Validate application dependencies and user-installed native packages before production use.

OL8-built revisions remain available during the migration, but they will be deprecated over time and deleted after a notified migration period. New service conda environment revisions will be built on OL9 only. No lifecycle date is implied by this page; follow OCI service notices for deprecation and deletion dates.

For a direct lookup from an active OL8-built revision to its OL9-built replacement, see [Migrate from an OL8-built Service Conda Environment to an OL9-built Revision](./ol8-to-ol9-service-conda-environments.md).

The trailing `_v1`, `_v2`, and similar values in a slug are pack revisions. Do not use the revision number alone to infer the build base; use the **Build base** column.

## Active environments

### Base environments

| Environment | Slug | Build base | Primary use case | Description |
|---|---|---|---|---|
| Python 3.10 Base environment | `python_p310_any_x86_64_v3` | Oracle Linux 9 (OL9) | Start from a minimal Python environment and add your own packages | Base Python 3.10 environment for customization. |
| Python 3.10 Base environment | `python_p310_any_x86_64_v2` | Oracle Linux 8 (OL8) | Start from a minimal Python environment and add your own packages | Base Python 3.10 environment for customization. |
| Python 3.11 Base environment | `python_p311_any_x86_64_v4` | Oracle Linux 9 (OL9) | Start from a minimal Python environment and add your own packages | Base Python 3.11 environment for customization. |
| Python 3.11 Base environment | `python_p311_any_x86_64_v3` | Oracle Linux 8 (OL8) | Start from a minimal Python environment and add your own packages | Base Python 3.11 environment for customization. |
| Python 3.12 Base environment | `python_p312_any_x86_64_v3` | Oracle Linux 9 (OL9) | Start from a minimal Python environment and add your own packages | Base Python 3.12 environment for customization. |
| Python 3.12 Base environment | `python_p312_any_x86_64_v2` | Oracle Linux 8 (OL8) | Start from a minimal Python environment and add your own packages | Base Python 3.12 environment for customization. |

### General-purpose machine learning

| Environment | Slug | Build base | Primary use case | Description |
|---|---|---|---|---|
| General Machine Learning for CPUs on Python 3.11 | `generalml_p311_cpu_x86_64_v6` | Oracle Linux 9 (OL9) | Broad CPU-based machine learning and data science workflows | General-purpose machine learning environment with Oracle data-access libraries and core ML packages such as scikit-learn, XGBoost, and LightGBM. |
| General Machine Learning for CPUs on Python 3.11 | `generalml_p311_cpu_x86_64_v5` | Oracle Linux 8 (OL8) | Broad CPU-based machine learning and data science workflows | General-purpose machine learning environment with Oracle data-access libraries and core ML packages such as scikit-learn, XGBoost, and LightGBM. |
| General Machine Learning for CPUs on Python 3.12 | `generalml_p312_cpu_x86_64_v4` | Oracle Linux 9 (OL9) | Broad CPU-based machine learning and data science workflows | General-purpose machine learning environment on Python 3.12 with Oracle integrations and common ML libraries for tabular and classical ML work. |
| General Machine Learning for CPUs on Python 3.12 | `generalml_p312_cpu_x86_64_v3` | Oracle Linux 8 (OL8) | Broad CPU-based machine learning and data science workflows | General-purpose machine learning environment on Python 3.12 with Oracle integrations and common ML libraries for tabular and classical ML work. |
| General Machine Learning for CPUs on Python 3.13 | `generalml_p313_cpu_x86_64_v1` | Oracle Linux 9 (OL9) | Broad CPU-based machine learning and data science workflows | General-purpose machine learning environment for Python 3.13. No active OL8-built revision is available. |
| General Machine Learning for CPUs on Python 3.14 | `generalml_p314_cpu_x86_64_v1` | Oracle Linux 9 (OL9) | Broad CPU-based machine learning and data science workflows | General-purpose machine learning environment for Python 3.14. No active OL8-built revision is available. |

### GPU deep learning and inference

| Environment | Slug | Build base | Primary use case | Description |
|---|---|---|---|---|
| PyTorch 2.8 for GPU on Python 3.12 | `pytorch28_p312_gpu_x86_64_v2` | Oracle Linux 9 (OL9) | PyTorch-based model training, fine-tuning, and deep learning workflows | GPU environment for PyTorch workloads, including CUDA support and commonly used libraries for transformer and LLM-oriented development. |
| PyTorch 2.8 for GPU on Python 3.12 | `pytorch28_p312_gpu_x86_64_v1` | Oracle Linux 8 (OL8) | PyTorch-based model training, fine-tuning, and deep learning workflows | GPU environment for PyTorch workloads, including CUDA support and commonly used libraries for transformer and LLM-oriented development. |
| TensorFlow 2.20 for GPU on Python 3.12 | `tensorflow220_p312_gpu_x86_64_v2` | Oracle Linux 9 (OL9) | TensorFlow training and inference on GPU | GPU environment for TensorFlow-based deep learning workflows, including TensorFlow, TensorBoard, and core data science packages. |
| TensorFlow 2.20 for GPU on Python 3.12 | `tensorflow220_p312_gpu_x86_64_v1` | Oracle Linux 8 (OL8) | TensorFlow training and inference on GPU | GPU environment for TensorFlow-based deep learning workflows, including TensorFlow, TensorBoard, and core data science packages. |
| ONNX Runtime on Python 3.12 with GPU support | `onnxruntime_p312_gpu_x86_64_v2` | Oracle Linux 9 (OL9) | GPU-backed ONNX inference workloads | Environment focused on ONNX model inference, with GPU-enabled ONNX Runtime and support for inference scenarios such as embeddings and text generation. |
| ONNX Runtime on Python 3.12 with GPU support | `onnxruntime_p312_gpu_x86_64_v1` | Oracle Linux 8 (OL8) | GPU-backed ONNX inference workloads | Environment focused on ONNX model inference, with GPU-enabled ONNX Runtime and support for inference scenarios such as embeddings and text generation. |

### Spark and Data Flow

| Environment | Slug | Build base | Primary use case | Description |
|---|---|---|---|---|
| PySpark 3.5 and Data Flow on Python 3.12 | `pyspark35_p312_cpu_x86_64_v2` | Oracle Linux 9 (OL9) | Spark, Data Flow, and large-scale data processing workflows | Recommended for Jobs on the OL9 runtime image. This revision passed Jobs, Model Deployment, and Notebook validation. |
| PySpark 3.5 and Data Flow on Python 3.12 | `pyspark35_p312_cpu_x86_64_v1` | Oracle Linux 8 (OL8) | Spark, Data Flow, and large-scale data processing workflows | Do not use this revision for Jobs on the OL9 runtime image. It failed OL9 Jobs validation because of a GDAL compatibility issue; use `pyspark35_p312_cpu_x86_64_v2` instead. |

### Operator-focused environments

| Environment | Slug | Build base | Primary use case | Description |
|---|---|---|---|---|
| AI Forecasting Operator | `forecast_p311_cpu_x86_64_v18` | Oracle Linux 9 (OL9) | Time-series forecasting workflows with Oracle ADS operator support | Forecasting environment with Oracle ADS, AutoMLX, and forecasting libraries such as Prophet, NeuralProphet, AutoTS, and pmdARIMA. |
| AI Forecasting Operator | `forecast_p311_cpu_x86_64_v17` | Oracle Linux 8 (OL8) | Time-series forecasting workflows with Oracle ADS operator support | Forecasting environment with Oracle ADS, AutoMLX, and forecasting libraries such as Prophet, NeuralProphet, AutoTS, and pmdARIMA. |
| AI Forecasting Operator Light | `forecast_light_p311_cpu_x86_64_v7` | Oracle Linux 9 (OL9) | Lightweight time-series forecasting workflows | Lighter forecasting environment for common time-series workflows with a smaller package set. |
| AI Forecasting Operator Light | `forecast_light_p311_cpu_x86_64_v6` | Oracle Linux 8 (OL8) | Lightweight time-series forecasting workflows | Lighter forecasting environment for common time-series workflows with a smaller package set. |

### ARM environments

| Environment | Slug | Build base | Primary use case | Description |
|---|---|---|---|---|
| ARM Pack for Machine Learning on Python 3.12 | `armml_p312_cpu_aarch64_v2` | Oracle Linux 9 (OL9) | Machine learning workflows on ARM-based notebook, job, pipeline, and deployment shapes | ARM-targeted machine learning environment for data access, classical ML, and ONNX-related workflows on ARM infrastructure. |
| ARM Pack for Machine Learning on Python 3.12 | `armml_p312_cpu_aarch64_v1` | Oracle Linux 8 (OL8) | Machine learning workflows on ARM-based notebook, job, pipeline, and deployment shapes | ARM-targeted machine learning environment for data access, classical ML, and ONNX-related workflows on ARM infrastructure. |

### Other catalog entries

The following revisions are active in the catalog snapshot used for this update but are not included in the OL9 migration test plan. Their build base is therefore not confirmed here.

| Environment | Slug | Build base | Primary use case | Description |
|---|---|---|---|---|
| AI Anomaly Detection Operator | `anomaly_p311_cpu_x86_64_v2` | Not confirmed | Anomaly detection workflows with Oracle ADS operator support | Operator-focused environment for building and running anomaly-detection workflows. |
| PySpark 3.5 and Data Flow on Python 3.11 | `pyspark35_p311_cpu_x86_64_v1` | Not confirmed | Spark, Data Flow, and large-scale data processing workflows | PySpark environment with Data Flow magic commands for working with remote Data Flow sessions from notebook sessions. |

## How to choose an environment

- Choose a **Base environment** if you want the lightest starting point and plan to install most of your own dependencies.
- Choose **General Machine Learning** if you want a broad default environment for CPU-based data science and machine learning work.
- Choose **PyTorch**, **TensorFlow**, or **ONNX Runtime** when your workflow is tied to one of those frameworks and you want a GPU-ready setup.
- Choose **PySpark and Data Flow** if your work depends on Spark sessions, distributed processing, or OCI Data Flow integration.
- Choose an **AI Forecasting Operator** environment for time-series forecasting with the Oracle ADS operator stack.
- Choose **ARM Pack for Machine Learning** only when you are working on ARM-based infrastructure.

After choosing an environment family, use the compatibility information above to select the appropriate build base, and validate the workload before production use.
