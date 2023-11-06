# 
import os
import oci

print("Job starts...")

# Resource Principal
dsc = None, None
COMPARTMENT_OCID = os.environ.get("PROJECT_COMPARTMENT_OCID", "UNDEFINED")
RP = os.environ.get("OCI_RESOURCE_PRINCIPAL_VERSION", "UNDEFINED")

if not RP or RP == "UNDEFINED":
    # Running locally
    config = oci.config.from_file("~/.oci/config", "DEFAULT")
    dsc = oci.data_science.DataScienceClient(config=config)
else:
    # Running as a job
    signer = oci.auth.signers.get_resource_principals_signer()
    dsc = oci.data_science.DataScienceClient(config={}, signer=signer)

# Check if the PROJECT_COMPARTMENT_OCID environment variable exists
if COMPARTMENT_OCID != "UNDEFINED":
    # lists all shapes in a given compartment
    shapes = dsc.list_job_shapes(compartment_id=COMPARTMENT_OCID)
    print(shapes.data)
else:
    print('The environment variable PROJECT_COMPARTMENT_OCID does not exist.')

print("Job Done.")
