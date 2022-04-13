import os
import oci

from flask import Flask, render_template, jsonify
from ads.common.oci_resource import OCIResource
from ads.jobs import Job
from ads.jobs.builders.infrastructure.dsc_job import DataScienceJobRun


app = Flask(__name__, template_folder=os.path.dirname(__file__))
config = oci.config.from_file()


@app.route("/")
@app.route("/<project_id>")
@app.route("/<compartment_id>/<project_id>")
def job_monitor(compartment_id=None, project_id=None):
    if project_id == "favicon.ico":
        return jsonify()
    tenancy_id = config["tenancy"]

    if project_id:
        if not compartment_id:
            compartment_id = OCIResource.get_compartment_id(project_id)

        if project_id == "all":
            project_id = None

        jobs = Job.datascience_job(
            compartment_id=compartment_id,
            project_id=project_id,
            lifecycle_state="ACTIVE",
            limit=20
        )
    else:
        jobs = []
        compartment_id = None

    compartments = oci.identity.IdentityClient(config=config).list_compartments(compartment_id=tenancy_id).data
    context = dict(
        jobs=jobs,
        compartment_id=compartment_id,
        project_id=project_id,
        compartments=compartments,
    )
    return render_template(
        'job_monitor.html',
        **context
    )


@app.route("/projects/<compartment_id>")
def list_projects(compartment_id):
    projects = oci.data_science.DataScienceClient(config=config).list_projects(compartment_id=compartment_id).data
    projects = sorted(projects, key=lambda x: x.display_name)
    context = {
        "compartment_id": compartment_id,
        "projects": [{"display_name": project.display_name, "ocid": project.id} for project in projects]
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
