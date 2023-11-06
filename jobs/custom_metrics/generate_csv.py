import argparse
import datetime
import oci
import os
import sys

dir = os.path.dirname(__file__)
sys.path.append(dir)
import query_helpers

DATETIME_DISPLAY_FORMAT = "%Y-%m-%d %H:%M:%S"

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("job_run_ocid", help="The OCID of the job run whose metrics should be queried.")
    parser.add_argument("--out", default="metrics.csv", help="The path to the output csv file. Defaults to metrics.csv")
    parser.add_argument("--namespace", help="The namespace to query for custom metrics. If unspecified, only service "
                                            "metrics will be queried.")
    parser.add_argument("--config", default="~/.oci/config",
                        help="The path to the OCI config file. Defaults to ~/.oci/config")
    parser.add_argument("--profile", default="DEFAULT",
                        help="The OCI config profile to use. Defaults to DEFAULT")
    parser.add_argument("--start-utc", default=datetime.datetime.utcnow() - datetime.timedelta(days=1),
                        type=datetime.datetime.fromisoformat,
                        help="The UTC start time for the metric query in ISO format. "
                             "Ex: 2023-01-31 or '2023-01-31 18:45:30'. Defaults to 24 hours ago.")
    parser.add_argument("--end-utc", default=datetime.datetime.utcnow(), type=datetime.datetime.fromisoformat,
                        help="The UTC end time for the metric query in ISO format. "
                             "Ex: 2023-01-31 or '2023-01-31 18:45:30'. Defaults to the current time.")
    args = parser.parse_args()

    config = oci.config.from_file(args.config, args.profile)
    monitoring_client = oci.monitoring.MonitoringClient(config=config)
    data_science_client = oci.data_science.DataScienceClient(config=config)

    print("Getting job run...")
    job_run = data_science_client.get_job_run(args.job_run_ocid).data

    print("Getting available metrics for job run...")
    service_metric_names = query_helpers.list_job_run_metrics(job_run, query_helpers.SERVICE_METRIC_NAMESPACE,
                                                              query_helpers.SERVICE_METRIC_OCID_DIMENSION,
                                                              monitoring_client)

    # Get the custom metric names if a namespace has been provided
    custom_metric_names = query_helpers.list_job_run_metrics(job_run, args.namespace,
                                                             query_helpers.CUSTOM_METRIC_OCID_DIMENSION,
                                                             monitoring_client) if args.namespace else []

    print(f"Querying metric values from {args.start_utc.strftime(DATETIME_DISPLAY_FORMAT)} UTC to "
          f"{args.end_utc.strftime(DATETIME_DISPLAY_FORMAT)} UTC and writing them to {args.out}")
    with open(args.out, 'w') as csv:
        csv.write("Name,Value,Namespace,Timestamp (UTC),Custom Dimensions\n")

        # Query service metrics and write them to the csv file.
        for m in service_metric_names:
            metric_summaries = query_helpers.get_metric_values(job_run, m, query_helpers.SERVICE_METRIC_NAMESPACE,
                                                               query_helpers.SERVICE_METRIC_OCID_DIMENSION,
                                                               monitoring_client, args.start_utc, args.end_utc)
            if len(metric_summaries) != 0:
                # The service currently includes the same set of dimensions on each job run metric, so we can
                # just use the first item in the list.
                for d in metric_summaries[0].aggregated_datapoints:
                    # Service metrics have no custom dimensions, so the last column is always empty.
                    csv.write(f"{m},{d.value},{query_helpers.SERVICE_METRIC_NAMESPACE},"
                              f"{d.timestamp.strftime(DATETIME_DISPLAY_FORMAT)},\n")

        # Query custom metrics and write them to the csv file.
        for m in custom_metric_names:
            custom_summaries = query_helpers.get_metric_values(job_run, m, args.namespace,
                                                               query_helpers.CUSTOM_METRIC_OCID_DIMENSION,
                                                               monitoring_client, args.start_utc, args.end_utc)
            for summary in custom_summaries:
                for d in summary.aggregated_datapoints:
                    custom_dimensions = {k: v for (k, v) in summary.dimensions.items()
                                         if k not in query_helpers.CUSTOM_METRIC_DEFAULT_DIMENSIONS}
                    custom_dimension_str = ';'.join('='.join((k, v)) for (k, v) in custom_dimensions.items())
                    csv.write(f"{m},{d.value},{args.namespace},{d.timestamp.strftime(DATETIME_DISPLAY_FORMAT)},"
                              f"{custom_dimension_str}\n")

    print("Complete")
