# Demonstrates a job that:
# + how to use the OCI SDK with a Job
# + how to initilize and use the OCI Resource Principal
# + how to initilize and use the OCI SDK Data Science Client

import os
import oci
import os

print("Job starts...")

# Resource Principal
dsc = None, None
COMPARTMENT_OCID = os.environ.get("PROJECT_COMPARTMENT_OCID", "UNDEFINED")
RP = os.environ.get("OCI_RESOURCE_PRINCIPAL_VERSION", "UNDEFINED")

if not RP or RP == "UNDEFINED":
    # LOCAL RUN
    config = oci.config.from_file("~/.oci/config", "BIGDATA")
    dsc = oci.data_science.DataScienceClient(config=config)
else:
    # JOB RUN
    signer = oci.auth.signers.get_resource_principals_signer()
    dsc = oci.data_science.DataScienceClient(config={}, signer=signer)

# If OCI SDK Client initilized
if not COMPARTMENT_OCID or COMPARTMENT_OCID != "UNDEFINED":
    shapes = dsc.list_job_shapes(compartment_id=COMPARTMENT_OCID)
    print(shapes.data[0])

print("Job Done.")
