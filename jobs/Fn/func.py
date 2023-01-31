import io
import json
import logging
import datetime
import sys

sys.path.append("/function")

from jobrunner import JobRunner
from fdk import response


def handler(ctx, data: io.BytesIO = None):
    try:
        print("Fn starting OCI Data Science Job Run...")
        # If triggered by OCI Event
        #
        # body = json.loads(data.getvalue())
        # print("event type: " + body["eventType"])
        # print("compartment name: " + body["data"]["compartmentName"])
        # print("compartment ocid: " + body["data"]["compartmentId"])
        # print("source ocid: " + body["data"]["resourceId"])

        print("Init Job Runner Class")
        jobrunner = JobRunner()
        # TODO: replace with your tenancy OCIDs!
        job_run = jobrunner.run_job(
            "ocid1.compartment.oc1..<>",
            "ocid1.datascienceproject.oc1.iad.<>",
            "ocid1.datasciencejob.oc1.iad.<>",
            job_run_name="Fn JobRun {}".format(str(datetime.datetime.utcnow())),
        )
        print("JobRun started, OCID: {}".format(job_run.data.id))
        print("Done!")
    except (Exception, ValueError) as ex:
        logging.getLogger().info("error parsing json payload: " + str(ex))

    return response.Response(
        ctx,
        response_data=json.dumps(
            {"message": "Started JobRun with OCID: {0}".format(job_run.data.id)}
        ),
        headers={"Content-Type": "application/json"},
    )
