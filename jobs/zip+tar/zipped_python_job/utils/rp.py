import os

OCI_RESOURCE_PRINCIPAL_VERSION = "OCI_RESOURCE_PRINCIPAL_VERSION"


def is_resource_principal():
    rp_version = os.environ.get(OCI_RESOURCE_PRINCIPAL_VERSION, "UNDEFINED")
    if rp_version == "UNDEFINED":
        # Runs Locally
        return False
    else:
        # Runs AS a JOB
        return True
