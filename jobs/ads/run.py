import ads, os
from ads.jobs import Job, DataScienceJob, PythonRuntime

# Setup your OCIDs!
COMPARTMENT_OCID = "ocid1.compartment.oc1..aaaaaaaa"
PROJECT_OCID = "ocid1.datascienceproject.oc1.iad.amaaaaaa"

LOG_GROUP_OCID = "ocid1.loggroup.oc1.iad.amaaaaaa"
# Optional
# LOG_OCID = "ocid1.log.oc1.iad.amaaaaaa"

BUCKET_NAME = ""
BUCKET_NAMESPACE = ""


# example of how to run jobs with Oracle ADS: https://accelerated-data-science.readthedocs.io/en/latest/user_guide/jobs/index.html
def run_and_monitor(artifact_name):
    """Create and run the ML Job for the generated artifact.

    Parameters
    ----------
    artifact_name : str
        Name of the artifact, returned by the `Export artifact` script.
    """

    # detect RP
    rp_version = os.environ.get("OCI_RESOURCE_PRINCIPAL_VERSION", "UNDEFINED")

    if not rp_version or rp_version == "UNDEFINED":
        # RUNs LOCALLY
        ads.set_auth("api_key", oci_config_location="~/.oci/config", profile="DEFAULT")
    else:
        # RUNs ON OCI
        ads.set_auth("resource_principal")

    print(f"Creating MLJob for {artifact_name}...")
    job = (
        Job(name="DataStudio to OCI-DS")
        .with_infrastructure(
            DataScienceJob()
            .with_log_group_id(LOG_GROUP_OCID)
            # .with_log_id(LOG_OCID)
            .with_compartment_id(COMPARTMENT_OCID)
            .with_project_id(PROJECT_OCID)
            # Optional
            # .with_subnet_id(SUBNET_OCID)
            .with_shape_name("VM.Standard2.1")
            .with_block_storage_size(50)
        )
        .with_runtime(
            PythonRuntime()
            .with_service_conda("pytorch110_p38_cpu_v1")
            .with_source(f"oci://{BUCKET_NAME}@{BUCKET_NAMESPACE}/tmp/{artifact_name}")
        )
    )
    job.create()

    print("Launching Job Run...")
    jobrun = job.run()
    jobrun.watch()


# if you want to run it directly
# run_and_monitor("hello_world_job.py")
