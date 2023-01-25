import os

OCI_RESOURCE_PRINCIPAL_VERSION = "OCI_RESOURCE_PRINCIPAL_VERSION"


def is_resource_principal():
    rp_version = os.environ.get(OCI_RESOURCE_PRINCIPAL_VERSION, "UNDEFINED")
    if not rp_version or rp_version == "UNDEFINED":
        # Runs locally
        return False
    else:
        # Runs as JOB
        return True
