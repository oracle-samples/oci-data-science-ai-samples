import oci
from datetime import datetime, timedelta
import logging

# logging.basicConfig(filename="jobs.log", encoding="utf-8", level=logging.DEBUG)
logging.basicConfig(level=logging.DEBUG)

# --- Set up
config_file = "~/.oci/config"
CONFIG_FILE = ""
ENV_TYPE = "DEFAULT"


class MJobs:
    def __init__(
        self, env_type, config_file, compartment_id, subnet_id, service_endpoint=None
    ):
        self.config_file = config_file
        self.compartment_id = compartment_id
        self.subnet_id = subnet_id

        try:
            logging.info("*** Setting up data science client....")
            self.oci_config = oci.config.from_file(self.config_file, env_type)
            self.identity = oci.identity.IdentityClient(config=self.oci_config)

            if service_endpoint == None:
                self.dsc = oci.data_science.DataScienceClient(config=self.oci_config)
            else:
                self.dsc = oci.data_science.DataScienceClient(
                    config=self.oci_config, service_endpoint=service_endpoint
                )
        except Exception as e:
            logging.error(e)
            raise e

    def create_project(self, compartment_id, project_name, project_description):
        logging.info("*** Creating Project ...")

        return self.dsc.create_project(
            create_project_details=oci.data_science.models.CreateProjectDetails(
                compartment_id=compartment_id,
                display_name=project_name,
                description=project_description,
            )
        )

    def list_projects(self, compartment_id):
        logging.info("*** List Projects ...")
        return self.dsc.list_projects(compartment_id)

    def create_job(
        self, compartment_id, project_id, job_name="Job", log_group=None, subnet_id=None
    ):
        logging.info("*** Creating Job ...")

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
            "jobLogConfigurationDetails": {
                "enableLogging": True,
                "enableAutoLogCreation": False,
                "logGroupId": log_group
                # "logGroupId": "<log_group_ocid>",
                # "logId": "<log_ocid>"
            },
            "jobInfrastructureConfigurationDetails": {
                # for custom VCN use "jobInfrastructureType": "STANDALONE",
                "jobInfrastructureType": "ME_STANDALONE",
                "shapeName": "VM.Standard2.1",
                "blockStorageSizeInGBs": "100",
                # "subnetId": subnet_id,
            },
        }
        return self.dsc.create_job(job_payload)

    def update_job(self, job_id, update_job_details=None):
        logging.info("*** Update Jobs ...")

        update_payload = {
            "displayName": "Update Job",
            "jobConfigurationDetails": {
                "jobType": "DEFAULT",
                "environmentVariables": {
                    "CONDA_ENV_TYPE": "service",
                    "CONDA_ENV_SLUG": "generalml_p38_cpu_v1",
                },
            },
            "jobInfrastructureConfigurationDetails": {
                "jobInfrastructureType": "STANDALONE",
                "shapeName": "VM.Standard2.2",
                "blockStorageSizeInGBs": "101",
            },
        }
        update_job_payload = (
            update_job_details if (update_job_details != None) else update_payload
        )
        return self.dsc.update_job(job_id=job_id, update_job_details=update_job_payload)

    def list_jobs(self, compartment_id, project_id):
        logging.info("*** List Jobs ...")

        return self.dsc.list_jobs(compartment_id=compartment_id, project_id=project_id)

    def get_job(self, job_id):
        logging.info("*** Get Job ...")

        return self.dsc.get_job(job_id)

    # NOTICE: Articat cannot be replaceds, once uploaded?
    def create_job_artifact(self, job_id, file_name):
        logging.info("*** Create Job Artifact ...")

        fstream = open(file_name, "rb")
        return self.dsc.create_job_artifact(
            job_id, fstream, content_disposition=f"attachment; filename={file_name}"
        )

    def get_job_artifact(self, job_id):
        logging.info("*** Get Job Artifact ...")

        return self.dsc.get_job_artifact_content(job_id=job_id)

    def head_job_artifact(self, job_id):
        logging.info("*** Head Job Artifact ...")

        return self.dsc.head_job_artifact(job_id=job_id)

    def change_job_compartment(self, job_id, compartment_id):
        logging.info("*** Change Job Compartment ...")

        compartment_details = {"compartmentId": compartment_id}

        return self.dsc.change_job_compartment(
            job_id=job_id, change_job_compartment_details=compartment_details
        )

    def delete_job(self, job_id):
        logging.info("*** Delete Job ...")

        return self.dsc.delete_job(job_id, delete_related_job_runs=True)

    def list_job_shapes(self, compartment_id):
        logging.info("*** List Job Shapes ...")

        return self.dsc.list_job_shapes(compartment_id=compartment_id)

    def run_job(self, compartment_id, project_id, job_id, job_run_name="Job Run"):
        logging.info("*** Run Job  ...")

        job_run_payload = {
            "projectId": project_id,
            "displayName": job_run_name,
            "jobId": job_id,
            "compartmentId": compartment_id,
            "jobConfigurationOverrideDetails": {
                "jobType": "DEFAULT",
                "environmentVariables": {
                    # "JOB_RUN_ENTRYPOINT": "job_arch/entry.py"
                    "CONDA_ENV_TYPE": "service",
                    "CONDA_ENV_SLUG": "generalml_p38_cpu_v1",
                    # "MY_ENV_VAR": "abcde"
                },
            },
            "jobLogConfigurationOverrideDetails": {
                # "logGroupId": log_id,
                "enableLogging": True,
                "enableAutoLogCreation": True,
            },
        }

        return self.dsc.create_job_run(job_run_payload)

    def list_job_runs(self, compartment_id, lifecycle_state=None):
        logging.info("*** List Job Runs ...")

        if lifecycle_state:
            return self.dsc.list_job_runs(
                compartment_id, lifecycle_state=lifecycle_state
            )
        else:
            return self.dsc.list_job_runs(compartment_id)

    def get_job_run(self, job_run_id):
        logging.info("*** Get Job Run ...")

        return self.dsc.get_job_run(job_run_id)

    def update_job_run(self, job_run_id, update_job_run):
        logging.info("*** Update Job Run ...")

        return self.dsc.update_job_run(
            job_run_id=job_run_id, update_job_run_details=update_job_run
        )

    def change_job_run_compartment(self, job_run_id, compartment_id):
        logging.info("*** Change Job Run Compartment ...")
        job_run_compartment_details = {"compartmentId": compartment_id}
        return self.dsc.change_job_run_compartment(
            job_run_id=job_run_id,
            change_job_run_compartment_details=job_run_compartment_details,
        )

    def cancel_job_run(self, job_run_id):
        logging.info("*** Cancel Job Run ...")

        return self.dsc.cancel_job_run(job_run_id=job_run_id)

    def delete_job_run(self, job_run_id):
        logging.info("*** Delete Job Run ...")

        return self.dsc.delete_job_run(job_run_id)
