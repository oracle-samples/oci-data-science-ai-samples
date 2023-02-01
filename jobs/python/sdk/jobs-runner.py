import oci
import argparse
import time
import os
from datetime import datetime, timedelta

from jobs import MJobs


def main(parser):
    parser.add_argument(
        "-f",
        "--file",
        required=True,
        default="",
        help="file to be used as job artifact",
    )

    args = parser.parse_args()
    file = args.file

    return {"file": file}


if __name__ == "__main__":
    """
    # RUN: python jobs-runner.py -f <../job+samples/example-filename.py>    
    """
    try:
        t = time.time()

        print("Start")
        parser = argparse.ArgumentParser()
        arguments = main(parser)

        print("------------------------------------------")
        print("FILE: {}".format(arguments["file"]))
        print("------------------------------------------")

        JOB_FILE = arguments["file"]

        # params
        project_id = os.environ["PROJECT"]
        compartment_id = os.environ["COMPARTMENT"]
        log_group_ocid = os.environ["LOGGROUP"]
        # subnet_id = os.environ["SUBNET"]
        tenant = os.environ["TENANCY"]
        config = os.environ["CONFIG"]

        # initialize
        # sdk = JobsRunner(tenant, config, compartment_id, subnet_id)
        sdk = MJobs(tenant, config, compartment_id,)

        job_id = ""
        job_name = "Job " + datetime.now().strftime("%m-%d-%Y %H:%M:%S")
        job = sdk.create_job(
            compartment_id=compartment_id,
            project_id=project_id,
            job_name=job_name,
            log_group=log_group_ocid,
        )

        print("Job ID: " + job.data.id)
        job_id = job.data.id
        print(job.data.id)

        artifact = sdk.create_job_artifact(job_id, JOB_FILE)

        job = sdk.get_job(job_id)
        print(job.data)

        job_run_name = "Job Run " + datetime.now().strftime("%m-%d-%Y %H:%M:%S")
        job_run = sdk.run_job(
            job.data.compartment_id,
            job.data.project_id,
            job.data.id,
            job_run_name=job_run_name,
        )
        print(job_run.data.id)
        job_run_id = job_run.data.id

        # job_runs = sdk.list_job_runs(compartment_id)
        # print(job_runs.data)

        # checks Job status every 10s
        while True:
            time.sleep(10)
            job_run_details = sdk.get_job_run(job_run_id)
            print(job_run_details.data)
            if job_run_details.data.lifecycle_state in ["IN_PROGRESS", "ACCEPTED"]:
                continue
            else:
                break

        #
        elapsed_time = time.time() - t
        print("Process Time: ", str(timedelta(seconds=elapsed_time)))
    except Exception as e:
        print("ERROR: ", e)
