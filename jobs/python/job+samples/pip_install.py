import datetime
import os
import sys
import subprocess
import oci

OCI_RESOURCE_PRINCIPAL_VERSION = "OCI_RESOURCE_PRINCIPAL_VERSION"

# env. variables send to the job by default!
TENANCY_OCID_KEY = "TENANCY_OCID"
PROJECT_OCID_KEY = "PROJECT_OCID"
PROJECT_COMPARTMENT_OCID_KEY = "PROJECT_COMPARTMENT_OCID"
JOB_OCID_KEY = "JOB_OCID"
JOB_COMPARTMENT_OCID_KEY = "JOB_COMPARTMENT_OCID"
JOB_ARTIFACT_FILE_NAME_KEY = "JOB_ARTIFACT_FILE_NAME"
JOB_RUN_OCID_KEY = "JOB_RUN_OCID"
JOB_RUN_COMPARTMENT_OCID_KEY = "JOB_RUN_COMPARTMENT_OCID"


class Job:
    def __init__(self):
        # Auto switch between key or resource princiapal, for local run or as job
        rp_version = os.environ.get(
            OCI_RESOURCE_PRINCIPAL_VERSION, "UNDEFINED")
        if not rp_version or rp_version == "UNDEFINED":
            # RUN LOCAL TEST
            self.signer = oci.config.from_file("~/.oci/config", "DEFAULT")
        else:
            # RUN AS JOB
            self.signer = oci.auth.signers.get_resource_principals_signer()

    def log(self, logs):
        for log in logs:
            print(log)

    def install(self, package):
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", package, "--user"])

    def get_by_key(self, key, default="LOCAL"):
        return os.environ.get(key, default)


if __name__ == "__main__":
    # Initilize
    job = Job()

    #
    job.log(
        [
            "Logging for job run: {}".format(
                job.get_by_key(JOB_RUN_OCID_KEY, "LOCAL")),
            "Current timestamp in UTC: {}".format(
                str(datetime.datetime.utcnow())),
        ]
    )

    print("Install custom sckit-learn and get the version!")

    # install custom library, if required
    job.install("scikit-learn")

    print("Finish Installation")

    # IMPORTANT: import cannot happen before the installation of the library
    import sklearn

    print("The scikit-learn version is {}.".format(sklearn.__version__))

    print("Job Done.")
