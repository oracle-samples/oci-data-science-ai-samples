import oci
import datetime
import os
from rp import is_resource_principal

OCI_RESOURCE_PRINCIPAL_VERSION = "OCI_RESOURCE_PRINCIPAL_VERSION"
JOB_RUN_OCID_KEY = "JOB_RUN_OCID"

#
class JobRunner:
    def __init__(self):
        # Auto switch between local and function
        if is_resource_principal() == False:
            # Used on your local machine
            self.signer = oci.config.from_file("~/.oci/config", "DEFAULT")
            self.dsc = oci.data_science.DataScienceClient(config=self.signer)
        else:
            # Will be used automatically when running as Function
            self.signer = oci.auth.signers.get_resource_principals_signer()
            self.dsc = oci.data_science.DataScienceClient(config={}, signer=self.signer)

    def run_job(self, compartment_id, project_id, job_id, job_run_name="Cron JobRun"):
        print("-------------------------------------")
        print("*** Run Job  ...")
        print("COMPARTMENT OCID: {}".format(compartment_id))
        print("PROJECT OCID: {}".format(project_id))
        print("JOB OCID: {}".format(job_id))

        job_run_payload = {
            "projectId": project_id,
            "displayName": job_run_name,
            "jobId": job_id,
            "compartmentId": compartment_id,
            "jobConfigurationOverrideDetails": {
                "jobType": "DEFAULT",
                "environmentVariables": {
                    # "JOB_RUN_ENTRYPOINT": "job_arch/entry.py"
                    # "CONTAINER_CUSTOM_IMAGE": "iad.ocir.io/oci/fn:1.0"
                    # "CONDA_ENV_TYPE": "service",
                    # "CONDA_ENV_SLUG": "mlcpuv1",
                    # "MY_ENV_VAR": "abcde"
                },
            },
        }

        return self.dsc.create_job_run(job_run_payload)
