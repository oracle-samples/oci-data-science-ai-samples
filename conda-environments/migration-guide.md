# Guide to migrate Data Science workloads to new service conda environments

This guide explains how to update a Data Science Notebook, Model Deployment, or Job after you select a new service conda environment.

- If you use a deprecated legacy environment, find its replacement in the [SCE compatibility matrix](./compatibility-matrix.md).
- If you use a latest active OL8-built environment, find its OL9-built revision in the [OL8-to-OL9 SCE migration lookup](./ol8-to-ol9-service-conda-environments.md).

After you identify the target SCE slug, follow the applicable workload instructions below.

## Data Science Notebook
Open the environment explorer inside the notebook and select one of the new supported conda environments.  Install the environment with the ```odsc conda install command``` inside a terminal.  Change the kernel to the new environment in the top right corner of the notebook.

## Model Deployment
For model deployments that use conda environments, the inference [conda environment](https://docs.oracle.com/iaas/Content/data-science/using/conda_understand_environments.htm) must be specified in the runtime.yaml file of the model artifact. This inference conda environment contains all model dependencies and is installed in the model server container. You can specify either one of the Data Science conda environments or a [published environment](https://docs.oracle.com/iaas/Content/data-science/using/conda_viewing.htm#conda-published) that you created. Follow the instructions to update the Model Deployment to use a new conda environment.
- [Prepare new model artifact](https://docs.oracle.com/iaas/Content/data-science/using/models-prepare-artifact.htm) by specifying the required conda pack in [runtime.yaml](https://docs.oracle.com/iaas/Content/data-science/using/model_runtime_yaml.htm).
- [Save model artifact in model catalog](https://docs.oracle.com/iaas/Content/data-science/using/models_saving_catalog.htm).
- [Update model deployment](https://docs.oracle.com/iaas/Content/data-science/using/model-dep-edit.htm) to use new model.

## Job
Jobs can run an entire Python project archived into a single file or [use one of the Data Science service conda environments](https://docs.oracle.com/en-us/iaas/Content/data-science/using/jobs-other.htm) as specified by the user. For a job whose service conda environment needs to be changed, follow these instructions.

> **PySpark 3.5 on the OL9 Jobs runtime:** If a Job uses `pyspark35_p312_cpu_x86_64_v1`, update it to `pyspark35_p312_cpu_x86_64_v2`. The OL8-built `v1` revision failed OL9 Jobs validation because of a GDAL compatibility issue; the OL9-built `v2` revision passed Jobs validation.

- Either [create a job](https://docs.oracle.com/iaas/Content/data-science/using/jobs-create.htm#jobs-create-console) and add this [custom environment variable](https://docs.oracle.com/en-us/iaas/Content/data-science/using/jobs-env-vars.htm) to specify a new supported Data Science conda environment
```
CONDA_ENV_TYPE => "service"
CONDA_ENV_SLUG = <service_conda_environment_slug>
```
- Or [start a job run](https://docs.oracle.com/iaas/Content/data-science/using/job-runs.htm#job-runs-start-console) and, to use a different conda environment for the job run, use the custom environment variables to override the job configuration.
