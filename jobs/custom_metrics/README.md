# Custom Metrics with Jobs

This sample demonstrates how to:
- Emit custom metrics from your Job Runs.
- Query service metrics and custom metrics for your Job Runs.

## Pre-requisites

You need a dynamic group that includes your job run resources.

Example matching rule:

```
all {resource.type='datasciencejobrun'}
```

You need a policy that enables resources in this dynamic group to post metrics.
See https://docs.oracle.com/iaas/Content/Identity/Reference/monitoringpolicyreference.htm

Example policy:

```
allow dynamic-group my_job_runs to use metrics in tenancy where target.metrics.namespace='my_custom_namespace'
```

You need a policy that enables your user to read metrics.
See https://docs.oracle.com/iaas/Content/Identity/Reference/monitoringpolicyreference.htm

Example policy:

```
allow group metric_reader_group to read metrics in compartment my_compartment
```

On your local machine, you need to install the OCI Python SDK: https://docs.oracle.com/en-us/iaas/tools/python/latest/

On your local machine, you need to setup an API Key: https://docs.oracle.com/iaas/Content/API/Concepts/apisigningkey.htm


## Overview of sample files

- The `artifact` directory contains all the files included in the job artifact.
  - The `custom_metrics` directory defines classes used to create the custom metrics.
    - `custom_metrics_provider.py` - Includes a base class for custom metric providers.
    - `gpu_metrics_provider.py` - Invokes `nvidia-smi` to query GPU properties and builds custom metrics for GPU power
                                  draw, temperature, GPU utilization, and memory usage.
    - `random_metrics_provider.py` - A very simple custom metric provider example that generates a random value.
  - `entrypoint.sh` - The job entrypoint script. It starts the `metrics_submitter.py` script in the background and then
                      sleeps for 10 minutes.
  - `metrics_submitter.py` - Every minute, this script invokes the GPU metrics provider and the random metrics provider.
                             The custom metrics are then pushed to the OCI Monitoring Service. This script uses
                             Resource Principal authentication to submit metrics.
- `generate_csv.py` - Queries metric values over the specified time interval and saves them to a csv file.
- `get_current_metrics.py` - Queries the current metric values of an ongoing job run. Refreshes the display every minute.
- `package_artifact.sh` - Creates the job artifact.
- `query_helpers.py` - Helper class with common methods used by both `generate_csv.py` and `get_current_metrics.py`.


## Running the sample

### Create the job artifact

To create the job artifact, navigate to the sample directory and run:

```
$ ./package_artifact.sh
```

This script will archive the contents of the `artifact` directory to `build/artifact.tar.gz`

### Create the job

Using the console, create a job. See https://docs.oracle.com/iaas/data-science/using/jobs-create.htm

For the job artifact, use the `build/artifact.tar.gz` file created in the previous step.

You must specify the following environment variables:
- `METRICS_NAMESPACE` - The namespace you want to store your custom metrics under. Each metric is associated with a
                        single namespace. The namespace to search must be provided when querying metrics later.
- `JOB_RUN_ENTRYPOINT` - Set this to `entrypoint.sh`.

If you select a standard shape or flex shape, the job run will only output a single custom metric named `random`.
If you select a GPU shape, the job run will emit the `random` metric as well as 4 custom GPU metrics:
  - `gpu.power_draw`
  - `gpu.temperature`
  - `gpu.gpu_utilization`
  - `gpu.memory_usage`

NOTE: The service does emit a GPU Utilization metric that averages the utilization of all GPU cards. With these custom
metrics, one metric is emitted per card, and the PCI Bus is added as a metric dimension to distinguish them. When
querying metrics, the aggregated data points are grouped by their dimensions. You can also include dimensions in your
MQL queries to filter your results, see https://docs.oracle.com/iaas/Content/Monitoring/Reference/mql.htm#dimension

For networking, if you choose to provide your own subnet, it must support egress to the OCI Monitoring Service, either
through a Service Gateway or a NAT Gateway.

Once you've created your job, you can start a job run.

### Query current metric values

Once your job run has reached the `IN PROGRESS` state, you can run `get_current_metrics.py` to query the current values
of the service metrics and custom metrics emitted by your job run.

The script will query the OCI Monitoring Service every minute.

This script uses API Key authentication to query metrics.

```
$ python ./get_current_metrics.py --help
usage: get_current_metrics.py [-h] [--namespace NAMESPACE] [--config CONFIG]
                              [--profile PROFILE]
                              job_run_ocid

positional arguments:
  job_run_ocid          The OCID of the job run whose metrics should be
                        displayed.

optional arguments:
  -h, --help            show this help message and exit
  --namespace NAMESPACE
                        The namespace to query for custom metrics. If
                        unspecified, only service metrics will be displayed.
  --config CONFIG       The path to the OCI config file. Defaults to
                        ~/.oci/config
  --profile PROFILE     The OCI config profile to use. Defaults to DEFAULT
```

Example invocation:

```
$ python ./get_current_metrics.py ocid1.datasciencejobrun.oc1.aaaaa --namespace my_namespace
```

### Save metrics to a csv file

If your job run has already completed, or if you're interested in viewing metric data over a given time interval, use
the `generate_csv.py` script.

This script uses API Key authentication to query metrics.

```
$ python ./generate_csv.py --help
usage: generate_csv.py [-h] [--out OUT] [--namespace NAMESPACE]
                       [--config CONFIG] [--profile PROFILE]
                       [--start-utc START_UTC] [--end-utc END_UTC]
                       job_run_ocid

positional arguments:
  job_run_ocid          The OCID of the job run whose metrics should be
                        queried.

optional arguments:
  -h, --help            show this help message and exit
  --out OUT             The path to the output csv file. Defaults to
                        metrics.csv
  --namespace NAMESPACE
                        The namespace to query for custom metrics. If
                        unspecified, only service metrics will be queried.
  --config CONFIG       The path to the OCI config file. Defaults to
                        ~/.oci/config
  --profile PROFILE     The OCI config profile to use. Defaults to DEFAULT
  --start-utc START_UTC
                        The UTC start time for the metric query in ISO format.
                        Ex: 2023-01-31 or '2023-01-31 18:45:30'. Defaults to
                        24 hours ago.
  --end-utc END_UTC     The UTC end time for the metric query in ISO format.
                        Ex: 2023-01-31 or '2023-01-31 18:45:30'. Defaults to
                        the current time.

```

Example invocation:

```
$ python ./generate_csv.py ocid1.datasciencejobrun.oc1.aaaaa --namespace my_namespace --start-utc '2023-01-05 18:00:00' --end-utc '2023-01-05 19:00:00'
```

### View metrics in the OCI console

If you prefer, you can craft metric queries in the OCI console and customize graphs displaying different metrics over
custom time ranges. See https://docs.oracle.com/iaas/Content/Monitoring/Tasks/buildingqueries.htm#console

## Expanding/Customizing the sample

### Implement the job run entrypoint

The `entrypoint.sh` script in this sample just sleeps after starting the metric submitter. You can replace the `sleep`
call with your own commands, or with calls to your own custom scripts.

If you want to include additional files in your job artifact, just copy them under the `artifact` directory. The
`package_artifact.sh` script will automatically include all files under this directory in the generated
`build/artifact.tar.gz` file.

### Define your own custom metrics

To define your own custom metrics:
- Create a class in the `artifact/custom_metrics` directory that that extends `CustomMetricsProvider`. Implement the
  `get_metrics()` function to produce your own custom metrics values.
- In `artifact/metrics_submitter.py`, initialize your custom metrics class in the `metric_providers` collection defined
  near the top of the file.

Use the existing `GpuMetricsProvider` and `RandomMetricsProvider` classes for reference.

## Additional Reading

OCI Data Science Jobs - https://docs.oracle.com/iaas/data-science/using/jobs-about.htm

OCI Monitoring Service - https://docs.oracle.com/iaas/Content/Monitoring/home.htm
