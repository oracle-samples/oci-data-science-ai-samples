import os
import re
import ads
import oci
import requests

from flask import Flask, render_template, jsonify, abort, request
from ads.common.oci_resource import OCIResource
from ads.common.oci_datascience import OCIDataScienceMixin
from ads.jobs import Job, DataScienceJobRun


OCI_KEY_CONFIG_LOCATION = os.environ.get("OCI_KEY_LOCATION", "~/.oci/config")
OCI_KEY_PROFILE_NAME = os.environ.get("OCI_KEY_PROFILE", "DEFAULT")
app = Flask(__name__, template_folder=os.path.dirname(__file__))


def instance_principal_available():
    try:
        requests.get(
            oci.auth.signers.InstancePrincipalsSecurityTokenSigner.GET_REGION_URL,
            headers=oci.auth.signers.InstancePrincipalsDelegationTokenSigner.METADATA_AUTH_HEADERS,
            timeout=1
        )
        return True
    except:
        return False


def get_authentication():
    """Returns a dictionary containing the authentication needed for initializing OCI client (e.g. DataScienceClient).
    This function checks if OCI API key config exists, if config exists, it will be loaded and used for authentication.
    If config does not exist, resource principal or instance principal will be used if available.
    To use a config at a non-default location, set the OCI_KEY_LOCATION environment variable.
    To use a non-default config profile, set the OCI_KEY_PROFILE_NAME environment variable.

    Returns
    -------
    dict
        A dictionary containing two keys: config and signer (optional).
        config is a dictionary containing api key authentication information.
        signer is an OCI Signer object for resource principal or instance principal authentication.
        IMPORTANT: signer will be returned only if config is not empty.

    Raises
    ------
    Exception
        When no authentication method is available.
    """
    if os.path.exists(os.path.expanduser(OCI_KEY_CONFIG_LOCATION)):
        auth = dict(
            config=oci.config.from_file(
                file_location=OCI_KEY_CONFIG_LOCATION,
                profile_name=OCI_KEY_PROFILE_NAME
            )
        )
    elif oci.auth.signers.resource_principals_signer.OCI_RESOURCE_PRINCIPAL_VERSION in os.environ:
        config = {}
        signer = oci.auth.signers.get_resource_principals_signer()
        auth = dict(config=config, signer=signer)
    elif instance_principal_available():
        config = {}
        signer = oci.auth.signers.InstancePrincipalsSecurityTokenSigner()
        auth = dict(config=config, signer=signer)
    else:
        raise Exception("Cannot determine authentication method.")
    return auth


auth = get_authentication()
if auth["config"]:
    ads.set_auth(oci_config_location=OCI_KEY_CONFIG_LOCATION, profile=OCI_KEY_PROFILE_NAME)
else:
    ads.set_auth('resource_principal')


def check_ocid(ocid):
    if not re.match(r'ocid[0-9].[a-z]+.oc[0-9].[a-z]{3}.[a-z0-9]+', ocid):
        abort(404, f"Invalid OCID: {ocid}")

def check_project_id(project_id):
    if not re.match(r'ocid[0-9].datascienceproject.oc[0-9].[a-z]{3}.[a-z0-9]+', project_id):
        abort(404, f"Invalid Project OCID: {project_id}")


def check_compartment_id(compartment_id):
    if not re.match(r'ocid[0-9].compartment.oc[0-9]..[a-z0-9]+', compartment_id):
        abort(404, f"Invalid Compartment OCID: {compartment_id}")


def check_compartment_project(compartment_id, project_id):
    if str(project_id).lower() == "all":
        project_id = None
    else:
        check_project_id(project_id)
        # Lookup compartment when project ID is valid but no compartment is given.
        if not compartment_id:
            compartment_id = OCIResource.get_compartment_id(project_id)
    check_compartment_id(compartment_id)
    return compartment_id, project_id

def check_endpoint():
    endpoint = request.args.get("endpoint")
    if endpoint:
        OCIDataScienceMixin.kwargs = {"service_endpoint": endpoint}
    else:
        OCIDataScienceMixin.kwargs = None
    return endpoint

def check_limit():
    limit = request.args.get("limit", 10)
    if isinstance(limit, str) and not limit.isdigit():
        abort(400, "limit parameter must be an integer.")
    return limit

def init_components(compartment_id, project_id):
    limit = request.args.get("limit", 10)
    endpoint = check_endpoint()

    if project_id:
        compartment_id, project_id = check_compartment_project(compartment_id, project_id)
    else:
        compartment_id = None

    auth = get_authentication()
    if auth["config"]:
        tenancy_id = auth["config"]["tenancy"]
    else:
        tenancy_id = auth["signer"].tenancy_id

    compartments = oci.identity.IdentityClient(**auth).list_compartments(compartment_id=tenancy_id).data
    context = dict(
        compartment_id=compartment_id,
        project_id=project_id,
        compartments=compartments,
        limit=limit,
        service_endpoint=endpoint,
    )
    return context


@app.route("/")
@app.route("/<project_id>")
@app.route("/<compartment_id>/<project_id>")
def job_monitor(compartment_id=None, project_id=None):
    if project_id == "favicon.ico":
        abort(404)

    context = init_components(compartment_id, project_id)
    return render_template(
        'job_monitor.html',
        **context
    )

@app.route("/jobs/<compartment_id>/<project_id>")
def list_jobs(compartment_id, project_id):
    compartment_id, project_id = check_compartment_project(compartment_id, project_id)
    limit = check_limit()
    endpoint = check_endpoint()

    # Calling OCI API here instead of ADS API is faster :)
    jobs = oci.data_science.DataScienceClient(
        service_endpoint=endpoint,
        **get_authentication()
    ).list_jobs(
        compartment_id=compartment_id,
        project_id=project_id,
        lifecycle_state="ACTIVE",
        sort_by="timeCreated",
        sort_order="DESC",
        limit=int(limit) + 5
    ).data[:int(limit)]

    job_list = []
    for job in jobs:
        job_data = dict(
            name=job.display_name,
            id=job.id,
            ocid=job.id,
            time_created=job.time_created.timestamp(),
            html=render_template("job_accordion.html", job=job)
        )
        job_list.append(job_data)
    return jsonify({
        "limit": limit,
        "jobs": job_list
    })


@app.route("/job_runs/<job_id>")
def list_job_runs(job_id):
    check_ocid(job_id)
    check_endpoint()
    job = Job.from_datascience_job(job_id)
    runs = job.run_list()
    run_list = []
    for run in runs:
        run_data = {
            "ocid": run.id,
            "job_ocid": job.id,
            "html": render_template("job_run_template.html", run=run, job=job)
        }
        run_list.append(run_data)
    return jsonify({
        "runs": run_list
    })

@app.route("/projects/<compartment_id>")
def list_projects(compartment_id):
    endpoint = check_endpoint()
    projects = oci.data_science.DataScienceClient(
        service_endpoint=endpoint,
        **get_authentication()
    ).list_projects(compartment_id=compartment_id).data
    projects = sorted(projects, key=lambda x: x.display_name)
    context = {
        "compartment_id": compartment_id,
        "projects": [
            {"display_name": project.display_name, "ocid": project.id} for project in projects
        ]
    }
    return jsonify(context)


def format_logs(logs):
    logs = sorted(logs, key=lambda x: x["time"] if x["time"] else "")
    for log in logs:
        if str(log["time"]).endswith("Z"):
            log["time"] = log["time"].split(".")[0].replace("T", " ")
        else:
            log["time"] = str(log["time"])
    logs = [log["time"] + " " + log["message"] for log in logs]
    print(f"{len(logs)} log messages.")
    return logs


@app.route("/logs/<job_run_ocid>")
def get_logs(job_run_ocid):
    print(f"Getting logs for {job_run_ocid}...")
    run = DataScienceJobRun.from_ocid(job_run_ocid)
    print(f"Status: {run.lifecycle_state} - {run.lifecycle_details}")
    if not run.log_id:
        logs = []
    else:
        logs = run.logs(limit=300)
        logs = format_logs(logs)
    context = {
        "ocid": job_run_ocid,
        "logs": logs,
        "status": run.lifecycle_state,
        "statusDetails": run.lifecycle_details,
        "stopped": True if run.lifecycle_state in DataScienceJobRun.TERMINAL_STATES else False
    }
    return jsonify(context)


@app.route("/delete/<job_ocid>")
def delete_job(job_ocid):
    check_endpoint()
    job = Job.from_datascience_job(job_ocid)
    try:
        job.delete()
        error = None
    except oci.exceptions.ServiceError as ex:
        error = ex.message
    return jsonify({
        "ocid": job_ocid,
        "error": error
    })
