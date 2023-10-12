import oci
import os
import logging

# logging.basicConfig(filename="jobs.log", encoding="utf-8", level=logging.DEBUG)
logging.basicConfig(level=logging.DEBUG)

# default location for the oci api auth key
config_file = "~/.oci/config"
CONFIG_FILE = ""
ENV_TYPE = ""


class MJobs:
    def __init__(self, env_type, config_file, compartment_id):
        self.config_file = config_file
        self.compartment_id = compartment_id
        # self.subnet_id = subnet_id

        try:
            logging.info("*** Setting up data science client....")

            # detect RP
            rp_version = os.environ.get("OCI_RESOURCE_PRINCIPAL_VERSION", "UNDEFINED")
            if not rp_version or rp_version == "UNDEFINED":
                # RUN LOCAL TEST
                self.signer = oci.config.from_file(config_file, env_type)
                self.dsc = oci.data_science.DataScienceClient(config=self.signer)
            else:
                # RUN ON OCI
                self.signer = oci.auth.signers.get_resource_principals_signer()
                self.dsc = oci.data_science.DataScienceClient(
                    config={}, signer=self.signer
                )
        except Exception as e:
            logging.error(e)
            raise e

    def create_project(self, compartment_id, project_name, project_description):
        logging.info("*** Creating project ...")

        return self.dsc.create_project(
            create_project_details=oci.data_science.models.CreateProjectDetails(
                compartment_id=compartment_id,
                display_name=project_name,
                description=project_description,
            )
        )

    def list_projects(self, compartment_id):
        logging.info("*** List projects ...")
        return self.dsc.list_projects(compartment_id)

    def create_job(self, compartment_id, project_id, job_name="Job", log_group=None):
        logging.info("*** Creating a Job ...")

        job_payload = {
            "projectId": project_id,
            "compartmentId": compartment_id,
            "displayName": job_name,
            "jobConfigurationDetails": {
                "jobType": "DEFAULT",
                "environmentVariables": {
                    # "CONDA_ENV_TYPE": "service",
                    # "CONDA_ENV_SLUG": "generalml_p38_cpu_v1"
                },
            },
            "jobLogConfigurationDetails": {
                "enableLogging": True,
                "enableAutoLogCreation": True,
                "logGroupId": log_group
                # "logId": "<log_id>"
            },
            "jobInfrastructureConfigurationDetails": {
                # for custom VCN use "jobInfrastructureType": "STANDALONE",
                "jobInfrastructureType": "ME_STANDALONE",
                "shapeName": "VM.Standard2.1",
                # For Flex Shapes Use
                # jobShapeConfigDetails: {
                #     ocpus: 4,
                #     memoryInGBs: 32
                # }
                "blockStorageSizeInGBs": "100"
                # Custom subnet is no longer required
                # "subnetId": subnet_id,
            },
        }
        return self.dsc.create_job(job_payload)

    # check fast jobs enabled shapes first!
    def create_fastjob(
        self,
        compartment_id,
        project_id,
        job_name="Job",
        jobShape="VM.Standard2.1",
        log_group=None,
    ):
        logging.info("*** Creating Fast Job ...")

        job_payload = {
            "projectId": project_id,
            "compartmentId": compartment_id,
            "displayName": job_name,
            "jobConfigurationDetails": {
                "jobType": "DEFAULT",
                "environmentVariables": {
                    # "CONDA_ENV_TYPE": "service",
                    # "CONDA_ENV_SLUG": "generalml_p38_cpu_v1"
                },
            },
            "jobLogConfigurationDetails": {
                "enableLogging": True,
                "enableAutoLogCreation": True,
                "logGroupId": log_group
                # "logId": "<log_id>"
            },
            "jobInfrastructureConfigurationDetails": {
                # for custom VCN use "jobInfrastructureType": "STANDALONE",
                "jobInfrastructureType": "ME_STANDALONE",
                "shapeName": jobShape,
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
                # for custom VCN use "jobInfrastructureType": "STANDALONE",
                "jobInfrastructureType": "ME_STANDALONE",
                "shapeName": "VM.Standard2.2",
                # For Flex Shapes Use
                # jobShapeConfigDetails: {
                #     ocpus: 4,
                #     memoryInGBs: 32
                # }
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
        logging.info("*** Get Job details ...")

        return self.dsc.get_job(job_id)

    # IMPORTANT: Currently Job artifacts cannot be replaced, once created!
    def create_job_artifact(self, job_id, file_name):
        logging.info("*** Create Job Artifact ...")

        fstream = open(file_name, "rb")
        return self.dsc.create_job_artifact(
            job_id,
            fstream,
            content_disposition=f"attachment; filename={os.path.basename(fstream.name)}",
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

    # all jobs shapes supported in the region
    def list_job_shapes(self, compartment_id):
        logging.info("*** List Job Shapes ...")

        return self.dsc.list_job_shapes(compartment_id=compartment_id)

    # List all available fast launch shapes in given region
    def list_fast_job_shapes(self, compartment_id):
        logging.info("*** List Fast Job Shapes ...")

        return self.dsc.list_fast_launch_job_configs(compartment_id=compartment_id)

    def run_job(
        self,
        compartment_id,
        project_id,
        job_id,
        job_run_name="Job Run",
    ):
        logging.info("*** Run Job  ...")

        job_run_payload = {
            "projectId": project_id,
            "displayName": job_run_name,
            "jobId": job_id,
            "compartmentId": compartment_id,
            "jobConfigurationOverrideDetails": {"jobType": "DEFAULT"}
            # Override the env. variables and log configs, if desired
            #
            # "jobConfigurationOverrideDetails": {
            #   "jobType": "DEFAULT",
            #   "environmentVariables": {
            #       "LOG_OBJECT_OCID": log_id,
            #       "JOB_RUN_ENTRYPOINT": "job_arch/entry.py"
            #       "CONTAINER_CUSTOM_IMAGE": "iad.ocir.io/tenancy-name/repo-name:tag"
            #       "CONDA_ENV_TYPE": "service",
            #       "CONDA_ENV_SLUG": "dataexpl_p37_cpu_v2",
            #       "MY_ENV_VAR": "abcde"
            #   },
            # },
            # "jobLogConfigurationOverrideDetails": {
            #   "logGroupId": log_id,
            #   "enableLogging": True,
            #   "enableAutoLogCreation": True,
            # },
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

    def list_job_runs_by(self, compartment_id, id):
        logging.info("*** List Job Runs By ...")
        return self.dsc.list_job_runs(compartment_id=compartment_id, id=id)

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
