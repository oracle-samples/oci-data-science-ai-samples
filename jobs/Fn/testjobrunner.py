import datetime
import os
from jobrunner import JobRunner

# env. variables available in all Jobs
PROJECT_OCID_KEY = "PROJECT_OCID"
PROJECT_COMPARTMENT_OCID_KEY = "PROJECT_COMPARTMENT_OCID"
JOB_OCID_KEY = "JOB_OCID"
JOB_COMPARTMENT_OCID_KEY = "JOB_COMPARTMENT_OCID"
JOB_ARTIFACT_FILE_NAME_KEY = "JOB_ARTIFACT_FILE_NAME"
JOB_RUN_OCID_KEY = "JOB_RUN_OCID"
JOB_RUN_COMPARTMENT_OCID_KEY = "JOB_RUN_COMPARTMENT_OCID"

if __name__ == "__main__":

    jobrunner = JobRunner()

    print(f'Start logging for job run: {os.environ.get(JOB_RUN_OCID_KEY, "LOCAL")}')
    print(f"Current timestamp in UTC: {str(datetime.datetime.utcnow())}")

    job_run = jobrunner.run_job(
        os.environ.get(JOB_COMPARTMENT_OCID_KEY, "ocid1.compartment...none"),
        os.environ.get(PROJECT_OCID_KEY, "ocid1.datascienceproject...none"),
        os.environ.get(JOB_OCID_KEY, "ocid1.datasciencejob..none"),
        job_run_name="Cron JobRun {}".format(str(datetime.datetime.utcnow())),
    )

    print(f"Started a JobRun with OCID: {job_run.data.id}")

    print("Done.")

