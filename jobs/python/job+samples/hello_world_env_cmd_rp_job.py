# Demonstrates a simple job that:
# - switches the OCI SDK key to resource principal when running as a Job
# - how to read the command line arguments
# - how to read the environment variables
# - how to use the OCI SDK

import os
import argparse
import oci
import os

# Resource Principal
TENANCY_OCID, dsc = None, None
COMPARTMENT_OCID = os.environ.get("PROJECT_COMPARTMENT_OCID", "UNDEFINED")
RP = os.environ.get("OCI_RESOURCE_PRINCIPAL_VERSION", "UNDEFINED")

if not RP or RP == "UNDEFINED":
    # LOCAL RUN
    config = oci.config.from_file("~/.oci/config", "BIGDATA")
    dsc = oci.data_science.DataScienceClient(config=config)
    TENANCY_OCID = config["tenancy"]
else:
    # JOB RUN
    signer = oci.auth.signers.get_resource_principals_signer()
    dsc = oci.data_science.DataScienceClient(config={}, signer=signer)
    TENANCY_OCID = signer.tenancy_id

# Command Line Arguments
parser = argparse.ArgumentParser()
parser.add_argument("-g", "--greeting", required=False, default="Hello")
args = parser.parse_args()

# print
print(
    f'{args.greeting} {os.environ.get("NAME", "UNKNOWN")} in tenancy OCID {TENANCY_OCID}'
)

# OCI SDK Client
if not COMPARTMENT_OCID or COMPARTMENT_OCID != "UNDEFINED":
    shapes = dsc.list_job_shapes(compartment_id=COMPARTMENT_OCID)
    print(shapes.data[0])
else:
    print("No PROJECT_COMPARTMENT_OCID set!")

print("Job Done.")
