import unittest
import logging
import os
from datetime import datetime, timedelta
from oci.data_science.models import job
from jobs import MJobs

unittest.TestLoader.sortTestMethodsUsing = None

logging.basicConfig(
    format="%(asctime)s : %(levelname)s : %(message)s",
    level=logging.INFO,
    filename="unit.log",
)


class JobsValueStorage:
    job = None
    job_get = None
    job_run = None
    job_run_get = None


# unittest.TestCase
class JobsTest:
    def __init__(self):
        logging.debug("Test the jobs class")
        self.array = []
        self.job_name = "Job " + datetime.now().strftime("%m-%d-%Y %H:%M:%S")
        self.job_run_name = "Run " + self.job_name
        self.project_id = os.environ["PROJECT"]
        self.compartment_id = os.environ["COMPARTMENT"]
        self.log_group_id = os.environ["LOGGROUP"]
        self.config = os.environ["CONFIG"]

        # self.project_id = "ocid1.datascienceproject.oc1.iad.amaaaaaanif7xwiana6leos7ajj42ilmedoaqlszup5dltbs37t6wn5tpdwa"
        # self.compartment_id = "ocid1.compartment.oc1..aaaaaaaafjjxtnycxa5b4xf76xn5f4nhl44kdafoxiecmxpp6mku3vty5mkq"
        # self.log_group_id = "ocid1.loggroup.oc1.iad.amaaaaaanif7xwiawjei2o7emubaggorbocxralx63dawx7flmzexlwyqodq"

        self.sdk = MJobs("DEFAULT", self.config, self.compartment_id)
        # self.assertTrue(True)

    def test_1_CreateJob(self):
        JobsValueStorage.job = self.sdk.create_job(
            compartment_id=self.compartment_id,
            project_id=self.project_id,
            job_name=self.job_name,
            log_group=self.log_group_id,
        )
        logging.debug(JobsValueStorage.job.data)
        # self.assertIsNotNone(JobsValueStorage.job)
        # self.assertTrue(JobsValueStorage.job.data.id.startswith("ocid1.datasciencejob"))

    def test_1_CreateFastJob(self):
        JobsValueStorage.job = self.sdk.create_fastjob(
            compartment_id=self.compartment_id,
            project_id=self.project_id,
            job_name=self.job_name,
            jobShape="VM.Standard2.1",
            log_group=self.log_group_id,
        )
        logging.debug(JobsValueStorage.job.data)

    def test_2_GetJob(self):
        JobsValueStorage.job_get = self.sdk.get_job(job_id=JobsValueStorage.job.data.id)
        # self.assertEqual(JobsValueStorage.job_get.data.id, JobsValueStorage.job.data.id)

    def test_3_ListJobs(self):
        jobs = self.sdk.list_jobs(
            compartment_id=self.compartment_id, project_id=self.project_id
        )
        # self.assertTrue(len(jobs.data) > 0)

    def test_4_UpdateJob(self):
        update_payload = {
            "displayName": "Update Job Unit "
            + datetime.now().strftime("%m-%d-%Y %H:%M:%S"),
            "jobConfigurationDetails": {
                "jobType": "DEFAULT",
                "environmentVariables": {
                    "CONDA_ENV_TYPE": "service",
                    "CONDA_ENV_SLUG": "generalml_p38_cpu_v1",
                },
            },
            "jobInfrastructureConfigurationDetails": {
                "jobInfrastructureType": "ME_STANDALONE",
                "shapeName": "VM.Standard2.2",
                "blockStorageSizeInGBs": "101",
            },
        }

        job = self.sdk.update_job(
            job_id=JobsValueStorage.job.data.id, update_job_details=update_payload
        )
        logging.info(job.data)
        # self.assertIsNotNone(job)

    # def test_5_ChangeJobCompartment(self):
    #     updated_job = self.sdk.change_job_compartment(
    #         JobsValueStorage.job.data.id,
    #         "ocid1.tenancy.oc1..<>",
    #     )
    #     print(updated_job)
    #     self.assertTrue(True)

    # artifacts
    def test_6_createJobArtifact(self):
        # dirname = os.path.dirname(os.path.abspath(__file__))
        # file = os.path.join(dirname, "hello_world_job.py")

        artifact = self.sdk.create_job_artifact(
            JobsValueStorage.job.data.id, "../job+samples/hello_world_job.py"
        )
        # self.assertIsNone(artifact)
        # self.assertTrue(True)
        print(artifact.data)

    def test_7_headJobArtifact(self):
        head = self.sdk.head_job_artifact(job_id=JobsValueStorage.job.data.id)
        print("head: {}".format(head))
        print("head.data: {}".format(head.data))
        print("head.headers: {}".format(head.headers))
        return None

    def test_8_getJobArtifactContent(self):
        response = self.sdk.get_job_artifact(JobsValueStorage.job.data.id)
        print(response)
        print(response.data)

        # storing the content into the download.py file
        # IMPORTANT for ZIP content you have to create ZIP file
        with open("download.py", "wb") as f:
            for chunk in response.data.raw.stream(1024 * 1024, decode_content=False):
                f.write(chunk)

        return None

    #
    def test_9_listJobShapes(self):
        shapes = self.sdk.list_job_shapes(self.compartment_id)
        print(shapes.data)
        return None

    def test_91_listFastJobShapes(self):
        shapes = self.sdk.list_fast_job_shapes(self.compartment_id)
        print(shapes.data)
        return None

    #
    def test_10_createJobRun(self):
        JobsValueStorage.job_run = self.sdk.run_job(
            compartment_id=self.compartment_id,
            project_id=self.project_id,
            job_id=JobsValueStorage.job.data.id,
        )
        return None

    def test_11_getJobRun(self):
        jobrun = self.sdk.get_job_run(JobsValueStorage.job_run.data.id)
        print(jobrun.data)
        return None

    def test_12_listJobRuns(self):
        job_run_list = self.sdk.list_job_runs(compartment_id=self.compartment_id)
        print(job_run_list.data)
        return None

    def test_12_listJobRunsBy(self):
        job_run_list = self.sdk.list_job_runs_by(
            compartment_id=self.compartment_id, id=self.project_id,
        )
        print(job_run_list.data)
        return None

    def test_13_updateJobRun(self):
        job_run_payload = {
            "displayName": "changed job run name",
            "freeformTags": {"key1": "test"},
        }
        self.sdk.update_job_run(
            JobsValueStorage.job_run.data.id, update_job_run=job_run_payload
        )
        return None

    # def test_14_changeJobRunCompartment(self):
    #     self.sdk.change_job_run_compartment(
    #         job_run_id=JobsValueStorage.job_run.data.id,
    #         compartment_id="ocid1.tenancy.oc1..<>",
    #     )
    #     return None

    # def test_15_cancelJobRun(self):
    #     cancel = self.sdk.cancel_job_run(job_run_id=JobsValueStorage.job_run.data.id)
    #     print(cancel.data)
    #     print(cancel.headers)
    #     return None

    # def test_16_deleteJobRun(self):
    #     delete = self.sdk.delete_job_run(job_run_id=JobsValueStorage.job_run.data.id)
    #     print(delete.data)
    #     print(delete.headers)
    #     return None

    # def test_99_DeleteJob(self):
    #     delete_job = self.sdk.delete_job(JobsValueStorage.job.data.id)
    #     print(delete_job)
    #     self.assertTrue(True)


# RUN WITH: python unit.py -vv
if __name__ == "__main__":
    # unittest.main()
    jobTest = JobsTest()
    jobTest.test_1_CreateJob()
    jobTest.test_2_GetJob()
    jobTest.test_3_ListJobs()
    jobTest.test_4_UpdateJob()
    jobTest.test_6_createJobArtifact()
    jobTest.test_7_headJobArtifact()
    jobTest.test_8_getJobArtifactContent()
    jobTest.test_9_listJobShapes()

    jobTest.test_10_createJobRun()
    jobTest.test_11_getJobRun()
    # jobTest.test_12_listJobRuns()
    # jobTest.test_12_listJobRunsBy()
    # jobTest.test_13_updateJobRun()

    # Can be ran only if the job run is still executing
    # jobTest.test_15_cancelJobRun()

    # NOTICE: you cannot delete Job Run during running or during cancelling!
    # jobTest.test_16_deleteJobRun()
    # jobTest.test_99_DeleteJob()
