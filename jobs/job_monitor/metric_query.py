import datetime
import oci.monitoring
import oci.data_science

SERVICE_METRIC_NAMESPACE = "oci_datascience_jobrun"
SERVICE_METRIC_OCID_DIMENSION = "resourceId"
CUSTOM_METRIC_OCID_DIMENSION = "job_run_ocid"
CUSTOM_METRIC_DEFAULT_DIMENSIONS = ["job_run_ocid", "job_ocid"]
SECONDS_IN_A_HOUR = 3600
SECONDS_IN_A_DAY = SECONDS_IN_A_HOUR * 24
SECONDS_IN_A_WEEK = SECONDS_IN_A_DAY * 7
SECONDS_IN_30_DAYS = SECONDS_IN_A_DAY * 30


def list_job_run_metrics(
    job_run: oci.data_science.models.JobRun,
    namespace: str,
    ocid_dimension: str,
    monitoring_client: oci.monitoring.MonitoringClient,
) -> list:
    """
    Lists the metrics available for the specified job run in the specified compartment and namespace

    Parameters
    ----------
    job_run: oci.data_science.models.JobRun
        The JobRun object whose available metrics should be queried.
    namespace: str
        The namespace to query for metrics.
    ocid_dimension: str,
        The name of the dimension to filter against using the job run OCID.
    monitoring_client: oci.monitoring.MonitoringClient
        The OCI Monitoring Service client

    Returns
    -------
    list
        A list of available metrics for the job run.
    """
    list_details = oci.monitoring.models.ListMetricsDetails(
        namespace=namespace, dimension_filters={ocid_dimension: job_run.id}
    )
    metrics = monitoring_client.list_metrics(job_run.compartment_id, list_details).data
    # The service response will include one item per unique combination of dimension values. We just want the unique
    # metric names here.
    metric_names = list(set([m.name for m in metrics]))
    return metric_names


def get_metric_values(
    job_run: oci.data_science.models.JobRun,
    name: str,
    namespace: str,
    ocid_dimension: str,
    monitoring_client: oci.monitoring.MonitoringClient,
    start: datetime.datetime = None,
    end: datetime.datetime = None,
) -> list:
    """
    Gets the metric values for the specified metric in the given time interval

    Parameters
    ----------
    job_run: oci.data_science.models.JobRun
        The JobRun object whose metrics should be queried.
    name: str
        The name of the metric to query.
    namespace: str
        The namespace for the metric.
    ocid_dimension: str,
        The name of the dimension to filter against using the job run OCID.
    monitoring_client: oci.monitoring.MonitoringClient
        The OCI Monitoring Service client
    start: datetime.datetime
        The start time for the metric query
    end: datetime.datetime
        The end time for the metric query

    Returns
    -------
    list
        The metric values. There will be one metric summary per unique combination of dimension values.
    """
    # OCI will only return 3 hours of data if the end time is not specified.
    # See limits: https://docs.oracle.com/en-us/iaas/Content/Monitoring/Reference/mql.htm#Interval
    if start and end:
        interval = (end - start).total_seconds()
        if interval < SECONDS_IN_A_HOUR:
            resolution = "1m"
        elif interval < SECONDS_IN_A_DAY:
            resolution = "5m"
        elif interval < SECONDS_IN_A_WEEK:
            resolution = "20m"
        else:
            resolution = "1h"
    else:
        resolution = "1m"
    response = monitoring_client.summarize_metrics_data(
        compartment_id=job_run.compartment_id,
        summarize_metrics_data_details=oci.monitoring.models.SummarizeMetricsDataDetails(
            namespace=namespace,
            resolution=resolution,
            query=f'{name}[{resolution}]{{{ocid_dimension} = "{job_run.id}"}}.mean()',
            start_time=start,
            end_time=end,
        ),
    )
    return response.data if response.data else []
