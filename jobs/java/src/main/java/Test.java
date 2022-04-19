import com.oracle.bmc.ConfigFileReader;
import com.oracle.bmc.Region;
import com.oracle.bmc.auth.AuthenticationDetailsProvider;
import com.oracle.bmc.auth.ConfigFileAuthenticationDetailsProvider;
import com.oracle.bmc.datascience.DataScienceClient;
import com.oracle.bmc.datascience.responses.CreateJobArtifactResponse;
import com.oracle.bmc.datascience.responses.CreateJobResponse;
import com.oracle.bmc.datascience.responses.CreateJobRunResponse;
import com.oracle.bmc.datascience.responses.GetJobResponse;
import com.oracle.bmc.datascience.model.*;
import com.oracle.bmc.datascience.requests.*;
import com.oracle.bmc.datascience.responses.*;

import java.io.IOException;
import java.util.List;

/**
 * Test the ML Jobs Java Client SDK
 */
public class Test {

    public static void main(String[] args) throws IOException {
        //
        System.out.println("Start Java ML Jobs Client Test");
        // TODO: Set the env. variables before testing!
        String CONFIG_LOCATION = System.getenv("CONFIG");
        String CONFIG_PROFILE = System.getenv("TENANCY");
        String COMPARTMENT_OCID = System.getenv("COMPARTMENT");
        String PROJECT_OCID = System.getenv("PROJECT");
        String SUBNET_OCID = System.getenv("SUBNET");
        String LOG_GROUP_UUID = System.getenv("LOGGROUP");

        System.out.println("* INIT");
        MLJobs client = new MLJobs(CONFIG_LOCATION,CONFIG_PROFILE,COMPARTMENT_OCID,PROJECT_OCID,SUBNET_OCID,LOG_GROUP_UUID);

        // Create Job with Managed Egress
        System.out.println("* CREATE JOB - MANAGED EGRESS");
        CreateJobResponse jobManagedEgress = client.createJobWithManagedEgress("Java Job - Managed Egress", COMPARTMENT_OCID, PROJECT_OCID);
        System.out.println(jobManagedEgress.getJob().getId());

        // Create Job
        System.out.println("* CREATE JOB");
        CreateJobResponse job = client.createJob("Java Job", COMPARTMENT_OCID, PROJECT_OCID, SUBNET_OCID);
        System.out.println(job.getJob().getId());

        // get Job UUID
        System.out.println("* GET JOB UUID");
        String jobUuid = job.getJob().getId();

        // Get Job By UUID
        System.out.println("* GET JOB By UUID");
        GetJobResponse jobDetails = client.getJob(jobUuid);
        System.out.println(jobDetails);
        System.out.println(jobDetails.getJob().getLifecycleState());
        System.out.println(jobDetails.getJob().getLifecycleDetails());

        // List Jobs
        System.out.println("* LIST JOBS");
        List<JobSummary> listJobs = client.listJobs();

        for (JobSummary jobSummary : listJobs) {
            System.out.println("ID: " + jobSummary.getId());
            System.out.println("Name: " + jobSummary.getDisplayName());
            System.out.println("Lifecycle State: " + jobSummary.getLifecycleState());
            System.out.println("Time Created: " + jobSummary.getTimeCreated());
        }


        System.out.println("* UPDATE JOB");
        UpdateJobResponse updateJobResponse = client.updateJob(jobUuid);
        System.out.println("Name: " + updateJobResponse.getJob().getDisplayName());

        // Create Artifact
        System.out.println("* CREATE ARTIFACT");
        CreateJobArtifactResponse jobArtifact = client.createJobArtifact(jobUuid);
        System.out.println(jobArtifact.getEtag());

        // Head Job Artifact
        System.out.println("* HEAD JOB ARTIFACT");
        HeadJobArtifactResponse headJobArtifactResponse = client.headJobArtifact(jobUuid);
        System.out.println("getOpcRequestId: " + headJobArtifactResponse.getOpcRequestId());

        // Get Job Artifact
        // TODO: how to download and store!

        // List Job Shapes
        System.out.println("* LIST JOB SHAPES");
        List<JobShapeSummary> shapes = client.listJobShapes();
        for (JobShapeSummary shape : shapes) {
            System.out.println("Name: " + shape.getName());
            System.out.println("Shape Series: " + shape.getShapeSeries());
            System.out.println("Core Count: " + shape.getCoreCount());
            System.out.println("Memory In GBs: " + shape.getMemoryInGBs());
        }

        // RUN JOB
        System.out.println("* RUN JOB");
        CreateJobRunResponse jobRunResponse = client.createJobRun(
                jobDetails.getJob().getId(),
                COMPARTMENT_OCID,
                PROJECT_OCID,
                "Java Job Run");
        System.out.println("JOB RUN CREATED: " + jobRunResponse.getJobRun().getId());

        System.out.println("* GET JOB RUN");
        GetJobRunResponse getJobRunResponse = client.getJobRun(jobRunResponse.getJobRun().getId());
        System.out.println("JOB RUN: " + getJobRunResponse.getJobRun().getId());

        // List Job Runs
        System.out.println("* LIST JOB RUNS");
        List<JobRunSummary> listJobRuns = client.listJobRuns();
        for (JobRunSummary jobRun : listJobRuns) {
            System.out.println("ID: " + jobRun.getId());
            System.out.println("Name: " + jobRun.getDisplayName());
        }

        // NOTICE: You cannot update a job while running the job.
        //        System.out.println("* UPDATE JOB RUN");
        //        UpdateJobRunResponse updateJobRunResponse = client.updateJobRun(jobRunResponse.getJobRun().getId());
        //        System.out.println("JOB RUN UPDATE: " + updateJobRunResponse.getJobRun().getDisplayName());

        // Cancel Job Run
        //        System.out.println("* CANCEL JOB RUN");
        //        CancelJobRunResponse cancelJobRunResponse = client.cancelJobRun(jobRunResponse.getJobRun().getId());
        //
        //        System.out.println("OpcRequestId: " + cancelJobRunResponse.getOpcRequestId());

        // If you did not cancel your job, you can monitor the Job run with this:
        client.monitorJobRun(jobRunResponse.getJobRun().getId());
    }
}
