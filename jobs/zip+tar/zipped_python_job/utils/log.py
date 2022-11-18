import oci
import datetime
import os
from utils.rp import is_resource_principal
from oci.loggingingestion import LoggingClient
from oci.loggingingestion.models import PutLogsDetails, LogEntryBatch, LogEntry

OCI_RESOURCE_PRINCIPAL_VERSION = "OCI_RESOURCE_PRINCIPAL_VERSION"
JOB_RUN_OCID_KEY = "JOB_RUN_OCID"

#
class Logging:
    def __init__(self):
        # Auto switch between local and job testing
        # rp_version = os.environ.get(OCI_RESOURCE_PRINCIPAL_VERSION, "UNDEFINED")
        if is_resource_principal() == False:
            # RUN LOCAL TEST
            self.signer = oci.config.from_file("~/.oci/config", "DEFAULT")
        else:
            # RUN AS JOB
            self.signer = oci.auth.signers.get_resource_principals_signer()

        # you can read env. variables here
        self.job_run_ocid = os.environ.get(JOB_RUN_OCID_KEY, "LOCAL")

    # Accepts logs as a list of strings - list is for the ability to send multiple entries in one batch
    def log(self, logs):
        for log in logs:
            print(log)
