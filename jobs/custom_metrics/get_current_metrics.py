import argparse
import curses
import datetime
import oci
import os
import sys
import time
from typing import Any

dir = os.path.dirname(__file__)
sys.path.append(dir)
import query_helpers

# When querying metrics, the smallest aggregation interval allowed is 1 minute.
# See https://docs.oracle.com/iaas/Content/Monitoring/Reference/mql.htm#Interval
REFRESH_INTERVAL_SECONDS = 60

METRIC_QUERY_WINDOW_MINUTES = 2

def display_current_metrics(stdscr: Any,
                            job_run_ocid: str,
                            namespace: str,
                            monitoring_client: oci.monitoring.MonitoringClient,
                            data_science_client: oci.data_science.DataScienceClient):
    """
    Displays the latest metrics for the specified job run

    Parameters
    ----------
    stdscr: Any
        The window object used for display
    job_run_ocid: str
        The job run OCID whose metrics should be displayed
    namespace: str
        The namespace to query for custom metrics. If None, only service metrics are displayed.
    monitoring_client: oci.monitoring.MonitoringClient
        The OCI Monitoring Service client
    data_science_client: oci.data_science.DataScienceClient
        The OCI Data Science Service client
    """

    # Initialize the display
    curses.noecho()
    stdscr.clear()
    stdscr.refresh()

    job_run_win = curses.newwin(3, curses.COLS - 1, 0, 0)
    job_run_win.scrollok(1)
    job_run_win.addnstr("Displaying metrics for job run:\n", curses.COLS - 1)
    job_run_win.addnstr(f"{job_run_ocid}\n", curses.COLS - 1)
    job_run_win.addnstr("Press Ctrl+C to exit.", curses.COLS - 1)
    job_run_win.refresh()

    refresh_win = curses.newwin(1, curses.COLS - 1, 4, 0)
    refresh_win.scrollok(1)
    refresh_win.clear()
    refresh_win.addnstr("Initializing...", curses.COLS - 1)
    refresh_win.refresh()

    # Get the job run
    job_run = data_science_client.get_job_run(job_run_ocid).data

    # Get the service metric names
    service_metric_names = query_helpers.list_job_run_metrics(job_run, query_helpers.SERVICE_METRIC_NAMESPACE,
                                                              query_helpers.SERVICE_METRIC_OCID_DIMENSION,
                                                              monitoring_client)
    if not service_metric_names:
        raise RuntimeError("No metrics available for job run. Ensure that the job run is in progress.")

    # Get the custom metric names if a namespace has been provided
    custom_metric_names = query_helpers.list_job_run_metrics(job_run, namespace,
                                                             query_helpers.CUSTOM_METRIC_OCID_DIMENSION,
                                                             monitoring_client) if namespace else []

    metrics_win = curses.newwin(1024, curses.COLS - 1, 6, 0)
    metrics_win.scrollok(1)
    countdown = 0
    while True:
        refresh_win.clear()

        if countdown == 0:
            refresh_win.addnstr(f"Refreshing metrics...", curses.COLS - 1)
            refresh_win.refresh()

            # Fetch and display service metrics
            metrics_win.clear()
            metrics_win.addnstr("Service Metrics\n", curses.COLS - 1)
            metrics_win.addnstr("---------------\n", curses.COLS - 1)

            end = datetime.datetime.utcnow()
            start = end - datetime.timedelta(minutes=METRIC_QUERY_WINDOW_MINUTES)
            for m in service_metric_names:
                metric_summaries = query_helpers.get_metric_values(job_run, m, query_helpers.SERVICE_METRIC_NAMESPACE,
                                                                   query_helpers.SERVICE_METRIC_OCID_DIMENSION,
                                                                   monitoring_client, start, end)
                # The service currently includes the same set of dimensions on each job run metric, so we can
                # just use the first item in the list.
                value = metric_summaries[0].aggregated_datapoints[-1].value if len(metric_summaries) > 0 else \
                    "No current value found"
                metrics_win.addnstr(f"{m}:  {value}\n", curses.COLS - 1)

            # Fetch and display custom metrics
            if custom_metric_names:
                metrics_win.addnstr("\nCustom Metrics\n", curses.COLS - 1)
                metrics_win.addnstr("--------------\n", curses.COLS - 1)
                for m in custom_metric_names:
                    custom_summaries = query_helpers.get_metric_values(job_run, m, namespace,
                                                                       query_helpers.CUSTOM_METRIC_OCID_DIMENSION,
                                                                       monitoring_client, start, end)
                    if not custom_summaries:
                        metrics_win.addnstr(f"{m}:  No current value found\n", curses.COLS - 1)

                    for summary in custom_summaries:
                        # Custom metrics can use custom dimensions, so we display this information to distinguish values
                        value = summary.aggregated_datapoints[-1].value if len(summary.aggregated_datapoints) > 0 \
                            else "No current value found"
                        custom_dimensions = {k:v for (k,v) in summary.dimensions.items()
                                             if k not in query_helpers.CUSTOM_METRIC_DEFAULT_DIMENSIONS}
                        custom_dimension_str = ';'.join('='.join((k,v)) for (k,v) in custom_dimensions.items())
                        metrics_win.addnstr(f"{m}:  {value}    {custom_dimension_str}\n", curses.COLS - 1)

            metrics_win.refresh()

            countdown = REFRESH_INTERVAL_SECONDS
        else:
            refresh_win.addnstr(f"Refreshing data in {countdown}s", curses.COLS - 1)
            refresh_win.refresh()
            countdown = countdown - 1

        time.sleep(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("job_run_ocid", help="The OCID of the job run whose metrics should be displayed.")
    parser.add_argument("--namespace", help="The namespace to query for custom metrics. If unspecified, only service "
                                            "metrics will be displayed.")
    parser.add_argument("--config", default="~/.oci/config",
                        help="The path to the OCI config file. Defaults to ~/.oci/config")
    parser.add_argument("--profile", default="DEFAULT",
                        help="The OCI config profile to use. Defaults to DEFAULT")
    args = parser.parse_args()
    config = oci.config.from_file(args.config, args.profile)
    monitoring_client = oci.monitoring.MonitoringClient(config=config)
    data_science_client = oci.data_science.DataScienceClient(config=config)

    try:
        curses.wrapper(display_current_metrics,
                       args.job_run_ocid,
                       args.namespace,
                       monitoring_client,
                       data_science_client)
    except KeyboardInterrupt:
        pass
