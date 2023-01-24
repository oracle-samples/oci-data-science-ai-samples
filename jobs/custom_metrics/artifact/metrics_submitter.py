import datetime
import oci
import os
import sys
import time

dir = os.path.dirname(__file__)
custom_metric_dir = os.path.join(dir, "custom_metrics")
sys.path.append(custom_metric_dir)
from custom_metrics_provider import Metric

if "METRICS_NAMESPACE" not in os.environ:
    raise RuntimeError("Required environment variable METRICS_NAMESPACE not set. Metrics will not be emitted.")

if "JOB_RUN_COMPARTMENT_OCID" not in os.environ:
    raise RuntimeError("This script must be run as part of a job run.")

METRIC_NAMESPACE = os.environ.get("METRICS_NAMESPACE")
METRIC_COMPARTMENT = os.environ.get("JOB_RUN_COMPARTMENT_OCID")

# When querying metrics, the smallest aggregation interval allowed is 1 minute.
# See https://docs.oracle.com/iaas/Content/Monitoring/Reference/mql.htm#Interval
METRIC_SUBMISSION_INTERVAL_SECONDS = 60

# Initialize custom metrics providers.
from gpu_metrics_provider import GpuMetricsProvider
from random_metrics_provider import RandomMetricsProvider
metric_providers = [
    GpuMetricsProvider(),
    RandomMetricsProvider()
]


def convert_to_metric_data_details(metric: Metric, timestamp: datetime.datetime) -> \
        oci.monitoring.models.MetricDataDetails:
    """
    Converts a Metric object into an oci.monitoring.models.MetricDataDetails object for submission to the Monitoring
    Service. In addition to the dimensions defined on the input Metric, the job ocid and job run ocid are also added
    as dimensions.

    Parameters
    ----------
    metric: Metric
        The Metric object to convert
    timestamp: datetime.datetime
        The timestamp to include on the metric datapoint

    Returns
    -------
    oci.monitoring.models.MetricDataDetails
        The oci.monitoring.models.MetricDataDetails object containing the metric details
    """
    dimensions = metric.dimensions
    dimensions["job_run_ocid"] = os.environ.get("JOB_RUN_OCID")
    dimensions["job_ocid"] = os.environ.get("JOB_OCID")
    return oci.monitoring.models.MetricDataDetails(
        namespace=METRIC_NAMESPACE,
        compartment_id=METRIC_COMPARTMENT,
        name=metric.name,
        dimensions=dimensions,
        datapoints=[
            oci.monitoring.models.Datapoint(
                timestamp=timestamp,
                value=metric.value,
                count=1)
        ]
    )


def submit_metrics(client: oci.monitoring.MonitoringClient) -> None:
    """
    Submit metrics to the Monitoring Service

    Parameters
    ----------
    client: oci.monitoring.MonitoringClient
        The OCI Monitoring Service client
    """
    metric_data_details = []
    timestamp = datetime.datetime.now()
    for provider in metric_providers:
        for metric in provider.get_metrics():
            metric_data_details.append(convert_to_metric_data_details(metric, timestamp))
    post_metric_details = oci.monitoring.models.PostMetricDataDetails(metric_data=metric_data_details)
    client.post_metric_data(post_metric_data_details=post_metric_details)


if __name__ == "__main__":
    signer = oci.auth.signers.get_resource_principals_signer()
    # The default "telemetry.<region>.oraclecloud.com" endpoint is for querying metrics.
    # Metrics should be submitted with the "telemetry-ingestion" endpoint instead.
    # See note here: https://docs.oracle.com/iaas/api/#/en/monitoring/20180401/MetricData/PostMetricData
    monitoring_client = oci.monitoring.MonitoringClient(
        config={},
        signer=signer,
        service_endpoint=f"https://telemetry-ingestion.{signer.region}.oraclecloud.com"
    )

    while True:
        submit_metrics(monitoring_client)
        time.sleep(METRIC_SUBMISSION_INTERVAL_SECONDS)
