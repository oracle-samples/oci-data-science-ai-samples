# Migrate from an OL8-built Service Conda Environment to an OL9-built Revision

## What is changing

OCI Data Science is rolling out an updated service runtime image based on Oracle Linux 9 (OL9). The rollout is phased by region and realm. Workloads created or updated after the rollout in a location will use the OL9 runtime image.

An SCE's **build base** identifies the Oracle Linux container used to build the SCE. It is different from the **runtime image** that OCI Data Science uses to run a notebook session, job, pipeline, or model deployment.

## Is customer action required?

Most customers do not need to change an SCE solely because of the runtime-image change. Customers can review these parts of their workloads for OL9 compatibility:

- custom conda environments and native packages used with notebook sessions;
- bring-your-own-container images, libraries, and dependencies used by jobs or model deployments; and
- scripts or external integrations that depend on operating-system-specific behavior.

This page focuses on OCI-provided service conda environments (SCEs). The latest OL8-built revisions listed here are generally intended to run with both OL8 and OL9 runtime images. Review documented exceptions, including the PySpark Jobs issue below. If your OL8-built SCE continues to work, you can keep using it during the migration period. OL8-built revisions will eventually be deprecated and deleted after a notified migration period. Future SCE revisions will be built on OL9 only, so plan and test the corresponding OL9-built revision when you are ready.

> **Required for PySpark 3.5 Jobs:** Jobs that use `pyspark35_p312_cpu_x86_64_v1` must move to `pyspark35_p312_cpu_x86_64_v2` before running on the OL9 Jobs runtime image. The OL8-built `v1` revision failed OL9 Jobs validation because of a GDAL compatibility issue. The OL9-built `v2` revision passed Jobs, Model Deployment, and Notebook validation.

## When to consider an OL9-built SCE

Consider migrating the SCE when:

- you are creating or updating a workload that will use the OL9 runtime image;
- your Job uses `pyspark35_p312_cpu_x86_64_v1` and will run on the OL9 Jobs runtime image;
- you encounter GLIBC, shared-library, native-package, or similar compatibility errors; or
- an OCI notification directs you to use an OL9-built SCE.

## Find the corresponding OL9-built revision

The following table contains confirmed OL8-to-OL9 migration pairs. When you choose to migrate the SCE, the OL9-built revision is the recommended target for workloads using the OL9 runtime image.

| Environment | Current OL8-built revision | OL9-built revision | Platform | Focus your validation on |
|---|---|---|---|---|
| Python 3.10 Base environment | `python_p310_any_x86_64_v2` | `python_p310_any_x86_64_v3` | Python 3.10, x86_64 | User-installed packages, compiled extensions, and operating-system library dependencies. |
| Python 3.11 Base environment | `python_p311_any_x86_64_v3` | `python_p311_any_x86_64_v4` | Python 3.11, x86_64 | User-installed packages, compiled extensions, and operating-system library dependencies. |
| Python 3.12 Base environment | `python_p312_any_x86_64_v2` | `python_p312_any_x86_64_v3` | Python 3.12, x86_64 | User-installed packages, compiled extensions, and operating-system library dependencies. |
| General Machine Learning for CPUs on Python 3.11 | `generalml_p311_cpu_x86_64_v5` | `generalml_p311_cpu_x86_64_v6` | Python 3.11, CPU, x86_64 | ADS and database connectivity, scikit-learn, XGBoost, LightGBM, model serialization, and native packages. |
| General Machine Learning for CPUs on Python 3.12 | `generalml_p312_cpu_x86_64_v3` | `generalml_p312_cpu_x86_64_v4` | Python 3.12, CPU, x86_64 | ADS and database connectivity, scikit-learn, XGBoost, LightGBM, model serialization, and native packages. |
| PySpark 3.5 and Data Flow on Python 3.12 | `pyspark35_p312_cpu_x86_64_v1` | `pyspark35_p312_cpu_x86_64_v2` | Python 3.12, CPU, x86_64 | Use `v2` for Jobs on the OL9 runtime image. The OL8-built `v1` failed OL9 Jobs validation because of a GDAL compatibility issue; `v2` passed Jobs, Model Deployment, and Notebook validation. |
| PyTorch 2.8 for GPU on Python 3.12 | `pytorch28_p312_gpu_x86_64_v1` | `pytorch28_p312_gpu_x86_64_v2` | Python 3.12, GPU, x86_64 | GPU detection, CUDA, model loading, training and inference, Transformers, PEFT, and custom extensions. |
| TensorFlow 2.20 for GPU on Python 3.12 | `tensorflow220_p312_gpu_x86_64_v1` | `tensorflow220_p312_gpu_x86_64_v2` | Python 3.12, GPU, x86_64 | GPU detection, model loading and saving, training and inference, TensorBoard, and custom operations. |
| ONNX Runtime on Python 3.12 with GPU support | `onnxruntime_p312_gpu_x86_64_v1` | `onnxruntime_p312_gpu_x86_64_v2` | Python 3.12, GPU, x86_64 | CUDA and cuDNN compatibility, GPU execution providers, model loading, inference outputs, and Transformers. |
| ARM Pack for Machine Learning on Python 3.12 | `armml_p312_cpu_aarch64_v1` | `armml_p312_cpu_aarch64_v2` | Python 3.12, CPU, aarch64 | ARM-native dependencies, database connectivity, ONNX workflows, model serialization, and representative inference. |
| AI Forecasting Operator | `forecast_p311_cpu_x86_64_v17` | `forecast_p311_cpu_x86_64_v18` | Python 3.11, CPU, x86_64 | ADS operator workflows, AutoMLX, forecasting libraries, data preparation, and model serialization. |
| AI Forecasting Operator Light | `forecast_light_p311_cpu_x86_64_v6` | `forecast_light_p311_cpu_x86_64_v7` | Python 3.11, CPU, x86_64 | ADS operator workflows, forecasting pipelines, data preparation, and model serialization. |

## Before you switch

The OL9-built revision is a newer SCE revision, not an operating-system-only rebuild that is guaranteed to have an identical package set. It can contain newer versions of ADS, database drivers, ML frameworks, CUDA libraries, or other dependencies. Review the environment details in Environment Explorer and test application behavior rather than assuming the two revisions are interchangeable.

OL9-built SCEs target the OL9 runtime image and can depend on newer system libraries. Do not use an OL9-built revision with the OL8 runtime image.

## Migrate and validate safely

1. Confirm that the OL9-built slug is available in Environment Explorer in your region.
2. Prepare a separate test path for the workload:
   - For a notebook session, install the OL9-built SCE without removing the working OL8-built SCE, and select it as the test notebook kernel.
   - For a job or pipeline, create a test configuration or run that references the OL9-built slug without changing the production configuration.
   - For a model deployment, prepare and save a test model artifact whose `runtime.yaml` references the OL9-built slug, and then create a non-production model deployment from that model.
3. Run import and startup checks for the libraries used by the workload.
4. Test data access, authentication, secrets, network access, and external service integrations.
5. Run a representative notebook, job, pipeline, training, or inference workflow end to end.
6. For GPU or native dependencies, verify device discovery and runtime library linkage.
7. After validation succeeds, update or promote the production kernel, configuration, pipeline step, or model artifact.
8. Keep the previous OL8-built configuration available as a rollback option during the migration period.

For update instructions for notebook sessions, model deployments, and jobs, see the [service conda environment migration guide](./migration-guide.md).

## If your environment is not listed

Do not infer the build base or OL9 replacement from the trailing revision number in an SCE slug. A higher `_v` number does not by itself mean that the environment was built on OL9.

If your current environment is not in the table, check the [active service conda environments](./service-conda-environments.md) and Environment Explorer. If no confirmed OL9-built pair is listed, contact Oracle Support before selecting a different environment family.

For migrations from a deprecated legacy SCE rather than from an active OL8-built revision, use the [SCE compatibility matrix](./compatibility-matrix.md).
