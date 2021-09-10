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
    def __init__(
        self, env_type, config_file, compartment_id, subnet_id, service_endpoint=None
    ):
        self.config_file = config_file
        self.compartment_id = compartment_id
        self.subnet_id = subnet_id

        try:
            print("*** Setting up data science client....")
            self.oci_config = oci.config.from_file(self.config_file, env_type)
            self.identity = oci.identity.IdentityClient(config=self.oci_config)

            if service_endpoint == None:
                self.dsc = oci.data_science.DataScienceClient(config=self.oci_config)
            else:
                self.dsc = oci.data_science.DataScienceClient(
                    config=self.oci_config, service_endpoint=service_endpoint
                )
        except Exception as e:
            print(e)
            raise e

    def create_project(self, compartment_id, project_name, project_description):
        print("-------------------------------------")
        print("*** Creating Project ...")

        return self.dsc.create_project(
            create_project_details=oci.data_science.models.CreateProjectDetails(
                compartment_id=compartment_id,
                display_name=project_name,
                description=project_description,
            )
        )

    def list_projects(self, compartment_id):
        print("-------------------------------------")
        print("*** List Projects ...")

        return self.dsc.list_projects(compartment_id)

    def create_job(self, compartment_id, project_id, job_name="Job", subnet_id=None):
        print("-------------------------------------")
        print("*** Creating Job ...")

        if subnet_id == None:
            subnet_id = self.subnet_id

        # TODO: Make sure shape etc are variables as well
        job_payload = {
            "projectId": project_id,
            "compartmentId": compartment_id,
            "displayName": job_name,
            "jobConfigurationDetails": {
                "jobType": "DEFAULT",
                "environmentVariables": {
                    # "CONDA_ENV_TYPE": "service",
                    # "CONDA_ENV_SLUG": "classic_cpu"
                },
            },
            # "jobLogConfigurationDetails": {
            #     "enableLogging": True,
            #     "enableAutoLogCreation": False,
            #     "logGroupId": "<log_group_id>",
            #     "logId": "<log_id>"
            # },
            "jobInfrastructureConfigurationDetails": {
                "jobInfrastructureType": "STANDALONE",
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

    # NOTICE: Articat cannot be replaceds, once uploaded?
    def create_job_artifact(self, job_id, file_name):
        print("-------------------------------------")
        print("*** Create Job Artifact ...")

        fstream = open(file_name, "rb")
        os.path.basename(fstream.name)
        return self.dsc.create_job_artifact(
            job_id, fstream, content_disposition=f"attachment; filename={os.path.basename(fstream.name)}"
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
                    # "LOG_OBJECT_OCID": log_id,
                    # "JOB_RUN_ENTRYPOINT": "job_arch/entry.py"
                    # "DOCKER_CUSTOM_IMAGE": "iad.ocir.io/ociodscdev/byod2:2.0"
                    # "CONDA_ENV_TYPE": "service",
                    # "CONDA_ENV_SLUG": "mlcpuv1",
                    # "MY_ENV_VAR": "abcde"
                },
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
    parser.add_argument("-t", "--tenant", required=True, default="", help='an tenancy to create and run the job')
    parser.add_argument("-f", "--file", required=True, default="", help='file to be used as job artifact')

    args = parser.parse_args()
    tenant = args.tenant
    file = args.file

    return {"tenant": tenant, "file": file}


if __name__ == "__main__":
    """
    # RUN: python mljobs.py -t <tenant> -f <file>    
    """
    try:
        t = time.time()

        print("Start")
        parser = argparse.ArgumentParser()
        arguments = main(parser)

        print("------------------------------------------")
        print("TENANT: {}".format(arguments["tenant"]))
        print("FILE: {}".format(arguments["file"]))
        print("------------------------------------------")

        ENV_TYPE = arguments["tenant"]
        JOB_FILE = arguments["file"]

        # parse config
        dirname = os.path.dirname(os.path.abspath(__file__))
        CONFIG_FILE = os.path.join(dirname, "config.ini")

        config = configparser.ConfigParser(allow_no_value=True)
        config.read(CONFIG_FILE)

        # params
        service_endpoint = config.get(ENV_TYPE, "service_endpoint")
        compartment_id = config.get(ENV_TYPE, "compartment_ocid")
        project_id = config.get(ENV_TYPE, "project_ocid")
        log_id = config.get(ENV_TYPE, "log_ocid")
        log_group_ocid = config.get(ENV_TYPE, "log_group_ocid")
        subnet_id = config.get(ENV_TYPE, "subnet_ocid")

        # initialize
        sdk = MLJobs(ENV_TYPE, config_file, compartment_id, subnet_id, service_endpoint)

        # project_id = sdk.create_project(compartment_id, "JOBS", "This project is used for the Jobs testing.")
        # print("Project OCID: {}".format(project_id.data))

        # print(sdk.list_projects())
        # sdk.list_projects()

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
