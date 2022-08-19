import oci
import time
import datetime
import os
import sys
import subprocess

OCI_RESOURCE_PRINCIPAL_VERSION = "OCI_RESOURCE_PRINCIPAL_VERSION"
JOB_RUN_OCID_KEY = "JOB_RUN_OCID"

# TODO: Replace with your topic OCID!
TOPIC_ID = "<onstopic_ocid>"

# NOTICE: Jobs trigger events on each lifecycle too!


class Job:
    def __init__(self):
        rp_version = os.environ.get(
            OCI_RESOURCE_PRINCIPAL_VERSION, "UNDEFINED")
        if not rp_version or rp_version == "UNDEFINED":
            # RUN LOCAL TEST
            self.signer = oci.config.from_file("~/.oci/config", "DEFAULT")
        else:
            # RUN AS JOB
            self.signer = oci.auth.signers.get_resource_principals_signer()

    def init_publisher(self):
        rp_version = os.environ.get(
            OCI_RESOURCE_PRINCIPAL_VERSION, "UNDEFINED")
        if rp_version == "UNDEFINED":
            # RUN LOCAL TEST
            self.ons_client = oci.ons.NotificationDataPlaneClient(
                config=self.signer)
        else:
            # RUN AS JOB
            self.ons_client = oci.ons.NotificationDataPlaneClient(
                config={}, signer=self.signer
            )

    def install(self, package):
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", package, "--user"])

    # https://docs.oracle.com/en-us/iaas/api/#/en/notification/20181201/NotificationTopic/PublishMessage
    def publish_message(self, title, body):
        return self.ons_client.publish_message(
            topic_id=TOPIC_ID,
            message_details=oci.ons.models.MessageDetails(
                body=body, title=title),
            opc_request_id=self.job_run_ocid,
        )


try:
    job = Job()

    try:
        print(
            "Start logging for job run: {}".format(
                os.environ.get(JOB_RUN_OCID_KEY, "LOCAL")
            )
        )
        print("Current timestamp in UTC: {}".format(
            str(datetime.datetime.utcnow())))

        print("Init publisher")

        job.init_publisher()

        print("Send Notification")

        publish_message_response = job.publish_message(
            "Job Finished",
            "This is a job OCID: {}".format(
                os.environ.get(JOB_RUN_OCID_KEY, "LOCAL")),
        )

        print("Published message response :{}".format(
            publish_message_response.data))

        print("Job Done.")
    except Exception as e:
        print(e)
        job.publish_message(
            "Job Failed",
            "Job OCID: {} \n failed with message: \n{}".format(
                os.getenv(JOB_RUN_OCID_KEY), e
            ),
        )
        print("Job Failed!")
        raise e
except Exception as e:
    raise e
