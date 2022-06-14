import oci
import datetime
import os
import time
import sys
import uuid
from oci.loggingingestion import LoggingClient
from oci.loggingingestion.models import PutLogsDetails, LogEntryBatch, LogEntry

OCI_RESOURCE_PRINCIPAL_VERSION = "OCI_RESOURCE_PRINCIPAL_VERSION"
JOB_RUN_OCID_KEY = "JOB_RUN_OCID"

# switch
class Job:
    def __init__(self):
        rp_version = os.environ.get(OCI_RESOURCE_PRINCIPAL_VERSION, "UNDEFINED")
        if not rp_version or rp_version == "UNDEFINED":
            # RUN LOCAL TEST
            self.signer = oci.config.from_file("~/.oci/config", "BIGDATA")
        else:
            # RUN AS JOB
            self.signer = oci.auth.signers.get_resource_principals_signer()


job = Job()

print(
    "Start logging for job run: {}".format(
        os.environ.get(JOB_RUN_OCID_KEY, "LOCAL")
    )
)
print("Current timestamp in UTC: {}".format(str(datetime.datetime.utcnow())))

print("Delay 5s")

time.sleep(5)

print("... another stdout")

print("Print all environment variables and values")

for item, value in os.environ.items():
    print("{}: {}".format(item, value))

print("Docker Job Done.")
