import oci
import argparse
import time
import configparser
import os
import sys
from datetime import datetime, timedelta

# --- Set up
config_file = "~/.oci/config"
CONFIG_FILE = ""
ENV_TYPE = ""


class MLJobs:
    def __init__(self, env_type, config_file, compartment_id, subnet_id):

        self.config_file = config_file
        self.compartment_id = compartment_id
        self.subnet_id = subnet_id

        try:
            print("*** Setting up data science client....")
            self.oci_config = oci.config.from_file(self.config_file, env_type)
            self.identity = oci.identity.IdentityClient(config=self.oci_config)
            self.dsc = oci.data_science.DataScienceClient(config=self.oci_config)
        except Exception as e:
            print(e)
            raise e

    def create_job(self, compartment_id, project_id, job_name="Job", subnet_id=None):
        print("-------------------------------------")
        print("*** Creating Job ...")

        if subnet_id == None:
            subnet_id = self.subnet_id

        job_payload = {
            "projectId": project_id,
            "compartmentId": compartment_id,
            "displayName": job_name,
            "jobConfigurationDetails": {
                "jobType": "DEFAULT",
                "environmentVariables": {
                    # SET env. variables
                    # "CONDA_ENV_TYPE": "service",
                    # "CONDA_ENV_SLUG": "generalml_p38_cpu_v1"
                },
            },
            # Sets the logging
            # "jobLogConfigurationDetails": {
            #     "enableLogging": True,
            #     "enableAutoLogCreation": False,
            #     "logGroupId": "<log_group_id>",
            #     "logId": "<log_id>"
            # },
            "jobInfrastructureConfigurationDetails": {
                # for custom VCN use "jobInfrastructureType": "STANDALONE",
                "jobInfrastructureType": "ME_STANDALONE",
                "shapeName": "VM.Standard2.1",
                "blockStorageSizeInGBs": "100",
                "subnetId": subnet_id,
            },
        }
        return self.dsc.create_job(job_payload)

    def list_jobs(self, compartment_id, project_id):
        print("-------------------------------------")
        print("*** List Jobs ...")

        return self.dsc.list_jobs(compartment_id=compartment_id, project_id=project_id)

    def get_job(self, job_id):
        print("-------------------------------------")
        print("*** Get Job ...")

        return self.dsc.get_job(job_id)

    # NOTICE: Artifacts cannot be replaced, once uploaded!
    def create_job_artifact(self, job_id, file_name):
        print("-------------------------------------")
        print("*** Create Job Artifact ...")

        fstream = open(file_name, "rb")
        os.path.basename(fstream.name)
        return self.dsc.create_job_artifact(
            job_id,
            fstream,
            content_disposition=f"attachment; filename={os.path.basename(fstream.name)}",
        )

    def run_job(
        self, compartment_id, project_id, job_id, log_id, job_run_name="Job Run"
    ):
        print("-------------------------------------")
        print("*** Run Job  ...")

        job_run_payload = {
            "projectId": project_id,
            "displayName": job_run_name,
            "jobId": job_id,
            "compartmentId": compartment_id,
            "jobConfigurationOverrideDetails": {
                "jobType": "DEFAULT",
                "environmentVariables": {
                    # "JOB_RUN_ENTRYPOINT": "<main_python_file>.py"
                    # "CONDA_ENV_TYPE": "service",
                    # "CONDA_ENV_SLUG": "generalml_p38_cpu_v1",
                    # "MY_ENV_VAR": "abcde"
                },
                "commandLineArguments": '100 linux "hi there"',
            },
            "jobLogConfigurationOverrideDetails": {
                "logGroupId": log_id,
                "enableLogging": True,
                "enableAutoLogCreation": True,
            },
        }

        return self.dsc.create_job_run(job_run_payload)

    def list_job_runs(self, compartment_id, lifecycle_state=None):
        print("-------------------------------------")
        print("*** List Job Runs ...")

        if lifecycle_state:
            return self.dsc.list_job_runs(
                compartment_id, lifecycle_state=lifecycle_state
            )
        else:
            return self.dsc.list_job_runs(compartment_id)

    def get_job_run(self, job_run_id):
        print("-------------------------------------")
        print("*** List Job Run ...")

        return self.dsc.get_job_run(job_run_id)

    def delete_job_run(self, job_run_id):
        print("-------------------------------------")
        print("*** Delete Job Run ...")

        return self.dsc.delete_job_run(job_run_id)

    def delete_job(self, job_id):
        print("-------------------------------------")
        print("*** Delete Job ...")

        return self.dsc.delete_job(job_id, delete_related_job_runs=True)


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
    # RUN: python mljobs.py -f <file>    
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
        subnet_id = os.environ["SUBNET"]
        tenant = os.environ["TENANCY"]
        config = os.environ["CONFIG"]

        # initialize
        sdk = MLJobs(tenant, config, compartment_id, subnet_id)

        job_id = ""
        job_name = "Job " + datetime.now().strftime("%m-%d-%Y %H:%M:%S")
        job = sdk.create_job(
            compartment_id=compartment_id, project_id=project_id, job_name=job_name
        )

        print("Job ID: " + job.data.id)
        job_id = job.data.id
        print(job.data.id)

        # artifact = sdk.create_job_artifact(job_id, "hello_world.py")
        artifact = sdk.create_job_artifact(job_id, JOB_FILE)

        job = sdk.get_job(job_id)
        print(job.data)

        job_run_name = "Job Run " + datetime.now().strftime("%m-%d-%Y %H:%M:%S")
        job_run = sdk.run_job(
            job.data.compartment_id,
            job.data.project_id,
            job.data.id,
            log_id=log_group_ocid,
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
