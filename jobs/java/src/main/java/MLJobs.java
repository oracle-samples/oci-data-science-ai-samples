import com.oracle.bmc.ConfigFileReader;
import com.oracle.bmc.Region;
import com.oracle.bmc.auth.AuthenticationDetailsProvider;
import com.oracle.bmc.auth.ConfigFileAuthenticationDetailsProvider;
import com.oracle.bmc.datascience.DataScienceClient;
import com.oracle.bmc.datascience.model.*;
import com.oracle.bmc.datascience.requests.*;
import com.oracle.bmc.datascience.responses.*;
import com.oracle.bmc.limits.LimitsClient;
import com.oracle.bmc.limits.model.LimitDefinitionSummary;
import com.oracle.bmc.limits.model.ServiceSummary;
import com.oracle.bmc.limits.requests.GetResourceAvailabilityRequest;
import com.oracle.bmc.limits.requests.ListLimitDefinitionsRequest;
import com.oracle.bmc.limits.requests.ListServicesRequest;
import com.oracle.bmc.limits.responses.GetResourceAvailabilityResponse;
import com.oracle.bmc.limits.responses.ListLimitDefinitionsResponse;
import com.oracle.bmc.limits.responses.ListServicesResponse;

import java.io.*;
import java.nio.file.StandardCopyOption;
import java.util.*;

/**
 * ML Jobs class implementing the OCI SDK Data Science Jobs Client API
 */
public class MLJobs {

    String CONFIG_LOCATION = "~/.oci/config";
    String CONFIG_PROFILE = "DEFAULT";
    String COMPARTMENT_OCID = "";
    String PROJECT_OCID = "";
    String SUBNET_OCID = "";
    String LOG_GROUP_UUID = "";

    DataScienceClient clientDataScience = null;
    LimitsClient limitsClient = null;

    MLJobs(String configLocation, String configProfile, String compartmentOCID, String projectOCID, String subnetOCID, String logGroupOCID) throws IOException {
        CONFIG_LOCATION = configLocation;
        CONFIG_PROFILE = configProfile;
        COMPARTMENT_OCID = compartmentOCID;
        PROJECT_OCID = projectOCID;
        SUBNET_OCID = subnetOCID;
        LOG_GROUP_UUID = logGroupOCID;

        ConfigFileReader.ConfigFile configWithProfile = ConfigFileReader.parse(CONFIG_LOCATION, CONFIG_PROFILE);
        final AuthenticationDetailsProvider provider =
                new ConfigFileAuthenticationDetailsProvider(configWithProfile);

        /*
         Old patter, which is now deprecated!
         clientDataScience = new DataScienceClient(provider);
         clientDataScience.setRegion(Region.US_ASHBURN_1);
        */
        clientDataScience = DataScienceClient.builder().region(Region.US_ASHBURN_1).build(provider);
        limitsClient = LimitsClient.builder().region(Region.US_ASHBURN_1).build(provider);
    }

    public void getLimitsDefinitions() {
        ListLimitDefinitionsResponse listLimitDefinitionsResponse= limitsClient.listLimitDefinitions(ListLimitDefinitionsRequest.builder().compartmentId("ocid1.tenancy.oc1..aaaaaaaa25c5a2zpfki3wo4ofza5l72aehvwkjbuavpnzqtmr4nigdgzi57a").build());
        List<LimitDefinitionSummary> l = listLimitDefinitionsResponse.getItems();
        for (LimitDefinitionSummary summary : l) {
            System.out.println("Name: " + summary.getName() + " - Service Name: " + summary.getServiceName());
        }
    }
    public void getLimits() {
        // compartmentId is the tenancy id
        GetResourceAvailabilityResponse r = limitsClient.getResourceAvailability(GetResourceAvailabilityRequest
                .builder()
                .compartmentId("ocid1.tenancy.oc1..aaaaaaaa")
                .serviceName("data-science")
                .limitName("ds-gpu-a10-count")
                .build()
        );

        System.out.println(r.getResourceAvailability().toString());
    }

    public CreateProjectResponse createProject() {
        CreateProjectDetails createProjectDetails =
                CreateProjectDetails.builder()
                        .displayName("Java Project")
                        .compartmentId(COMPARTMENT_OCID)
                        .description("Java Project Description")
                        .build();
        CreateProjectRequest createProjectRequest =
                CreateProjectRequest.builder().createProjectDetails(createProjectDetails).build();
        CreateProjectResponse createProjectResponse = clientDataScience.createProject(createProjectRequest);

        // System.out.println(createProjectResponse.getProject().getId());
        return createProjectResponse;
    }

    public List<JobShapeSummary> listJobShapes() {
        ListJobShapesRequest.Builder listJobShapesBuilder = ListJobShapesRequest.builder().compartmentId(COMPARTMENT_OCID);
        ListJobShapesRequest listJobShapesRequest = listJobShapesBuilder.build();
        ListJobShapesResponse listJobShapesResponse = clientDataScience.listJobShapes(listJobShapesRequest);

        return listJobShapesResponse.getItems();
    }

    public List<ProjectSummary> listProjects() {
        ListProjectsRequest.Builder listProjectsBuilder = ListProjectsRequest.builder().compartmentId(COMPARTMENT_OCID);
        ListProjectsRequest listProjectsRequest = listProjectsBuilder.build();
        ListProjectsResponse listOfProjects = clientDataScience.listProjects(listProjectsRequest);

        return listOfProjects.getItems();
    }

    public List<JobSummary> listJobs() {
        ListJobsRequest listJobsRequest = ListJobsRequest.builder().compartmentId(COMPARTMENT_OCID).build();
        return clientDataScience.listJobs(listJobsRequest).getItems();
    }

    public List<JobRunSummary> listJobRuns() {
        ListJobRunsRequest listJobRunsRequest = ListJobRunsRequest.builder().compartmentId(COMPARTMENT_OCID).build();
        return clientDataScience.listJobRuns(listJobRunsRequest).getItems();
    }

    public CreateJobResponse createJob(String jobName, String compartmentUuid,
                                       String projectUuid, String subnetUuid) throws IOException {

        CreateJobRequest createJobRequest = null;

        Map<String, String> envVariables = new HashMap<String, String>();
        envVariables.put("CONDA_ENV_TYPE", "service");
        envVariables.put("CONDA_ENV_SLUG", "generalml_p38_cpu_v1");

        // mounts storages - coming soon
//        List<JobStorageMountConfigurationDetails> jobStorageMountConfigurationDetails = new ArrayList<>();
//        jobStorageMountConfigurationDetails.add(
//                ObjectStorageMountConfigurationDetails
//                        .builder()
//                        .bucket("beta")
//                        .namespace("bucket-namespace")
//                        .destinationDirectoryName("beta").build());

        CreateJobDetails jobRequestDetails = CreateJobDetails.builder()
                .displayName(jobName)
                .projectId(projectUuid)
                .compartmentId(compartmentUuid)
                .jobConfigurationDetails(
                        DefaultJobConfigurationDetails
                                .builder()
                                .environmentVariables(envVariables)
                                .build())
//                .jobStorageMountConfigurationDetailsList(jobStorageMountConfigurationDetails)
                .jobInfrastructureConfigurationDetails(
                        StandaloneJobInfrastructureConfigurationDetails
                                .builder()
                                .shapeName("VM.Standard2.1")
                                .blockStorageSizeInGBs(100)
                                .subnetId(subnetUuid).build()).build();

        createJobRequest = CreateJobRequest.builder().createJobDetails(jobRequestDetails).build();
        return clientDataScience.createJob(createJobRequest);
    }

    public CreateJobResponse createJobWithManagedEgress(String jobName, String compartmentUuid,
                                                        String projectUuid) throws IOException {

        CreateJobRequest createJobRequest = null;

        Map<String, String> envVariables = new HashMap<String, String>();
        envVariables.put("CONDA_ENV_TYPE", "service");
        envVariables.put("CONDA_ENV_SLUG", "generalml_p38_cpu_v1");

        CreateJobDetails jobRequestDetails = CreateJobDetails.builder()
                .displayName(jobName)
                .projectId(projectUuid)
                .compartmentId(compartmentUuid)
                .jobConfigurationDetails(
                        DefaultJobConfigurationDetails
                                .builder()
                                .environmentVariables(envVariables)
                                .build())
                .jobInfrastructureConfigurationDetails(
                        ManagedEgressStandaloneJobInfrastructureConfigurationDetails
                                .builder()
                                .shapeName("VM.Standard2.1")
                                .blockStorageSizeInGBs(100).build()
                ).build();

        createJobRequest = CreateJobRequest.builder().createJobDetails(jobRequestDetails).build();
        return clientDataScience.createJob(createJobRequest);
    }

    public CreateJobArtifactResponse createJobArtifact(String JOB_UUID)
            throws IOException {

        final File jobArtifactFile = new File("src/main/java/hello_world_job.py");
        final InputStream in = new FileInputStream(jobArtifactFile);

        String filename = jobArtifactFile.getName();
        System.out.println("File name: " + filename);

        CreateJobArtifactRequest createJobArtifactRequest =
                CreateJobArtifactRequest.builder()
                        .jobArtifact(in)
                        .contentDisposition("attachment; filename=hello_world_job.py")
                        .jobId(JOB_UUID)
                        .build();
        return clientDataScience.createJobArtifact(createJobArtifactRequest);
    }

    public void getJobArtifact(String jobUUID) throws IOException {
        GetJobArtifactContentRequest getJobArtifactContentRequest = GetJobArtifactContentRequest.builder().jobId(jobUUID).build();
        GetJobArtifactContentResponse getJobArtifactContentResponse = clientDataScience.getJobArtifactContent(getJobArtifactContentRequest);

        final InputStream inputStream = getJobArtifactContentResponse.getInputStream();

        File targetFile = new File("src/temporary.py");

        java.nio.file.Files.copy(
                inputStream,
                targetFile.toPath(),
                StandardCopyOption.REPLACE_EXISTING);
    }

    public HeadJobArtifactResponse headJobArtifact(String jobUUID) {
        HeadJobArtifactRequest headJobArtifactRequest = HeadJobArtifactRequest.builder().jobId(jobUUID).build();
        return clientDataScience.headJobArtifact(headJobArtifactRequest);
    }

    public GetJobResponse getJob(String JOB_UUID) {
        GetJobRequest getJObRequest = GetJobRequest.builder().jobId(JOB_UUID).build();
        return clientDataScience.getJob(getJObRequest);
    }

    public UpdateJobResponse updateJob(String jobUUID) {
        UpdateJobDetails updateJobDetails = UpdateJobDetails.builder()
                .displayName("Java Job Update")
                .jobInfrastructureConfigurationDetails(
                        StandaloneJobInfrastructureConfigurationDetails
                                .builder()
                                .shapeName("VM.Standard2.1")
                                .blockStorageSizeInGBs(101)
                                .build()
                )
                .description("Change description")
                .build();

        UpdateJobRequest updateJobRequest = UpdateJobRequest
                .builder()
                .jobId(jobUUID)
                .updateJobDetails(updateJobDetails)
                .build();

        return clientDataScience.updateJob(updateJobRequest);
    }

    public ChangeJobCompartmentResponse changeJobCompartment(String jobUUID, String compartmentUUID) {
        ChangeJobCompartmentDetails changeJobCompartmentDetails = ChangeJobCompartmentDetails.builder()
                .compartmentId(compartmentUUID)
                .build();

        ChangeJobCompartmentRequest changeJobCompartmentRequest = ChangeJobCompartmentRequest
                .builder()
                .jobId(jobUUID)
                .changeJobCompartmentDetails(changeJobCompartmentDetails)
                .build();

        return clientDataScience.changeJobCompartment(changeJobCompartmentRequest);
    }

    public GetJobRunResponse getJobRun(String JOB_RUN_UUID) {
        GetJobRunRequest getJobRunRequest =
                GetJobRunRequest.builder().jobRunId(JOB_RUN_UUID).build();

        return clientDataScience.getJobRun(getJobRunRequest);
    }

    public CreateJobRunResponse createJobRun(String jobUuid,
                                             String compartmentUuid,
                                             String projectUuid,
                                             String jobRunName) {
        Map<String, String> envVariables = new HashMap<String, String>();
        envVariables.put("CONDA_ENV_TYPE", "service");
        envVariables.put("CONDA_ENV_SLUG", "generalml_p38_cpu_v1");


        CreateJobRunRequest createJobRunRequest =
                CreateJobRunRequest.builder()
                        .createJobRunDetails(
                                CreateJobRunDetails.builder()
                                        .jobId(jobUuid)
                                        .compartmentId(compartmentUuid)
                                        .projectId(projectUuid)
                                        .displayName(jobRunName)
                                        .jobConfigurationOverrideDetails(
                                                DefaultJobConfigurationDetails
                                                        .builder()
                                                        .environmentVariables(envVariables)
                                                        .build())
                                        .build())
                        .build();
        return clientDataScience.createJobRun(createJobRunRequest);
    }

    public UpdateJobRunResponse updateJobRun(String jobRunUUID) {
        Map<String, String> freeFormTags = new HashMap<String, String>();
        freeFormTags.put("key1", "value1");

        UpdateJobRunDetails updateJobRunDetails = UpdateJobRunDetails.builder()
                .displayName("Java Job Update")
                .freeformTags(freeFormTags)
                .build();

        UpdateJobRunRequest updateJobRunRequest = UpdateJobRunRequest
                .builder()
                .jobRunId(jobRunUUID)
                .updateJobRunDetails(updateJobRunDetails)
                .build();

        return clientDataScience.updateJobRun(updateJobRunRequest);
    }

    public ChangeJobRunCompartmentResponse changeJobRunCompartment(String jobRunUUID, String compartmentUUID) {
        ChangeJobRunCompartmentDetails changeJobRunCompartmentDetails = ChangeJobRunCompartmentDetails.builder()
                .compartmentId(compartmentUUID)
                .build();

        ChangeJobRunCompartmentRequest changeJobRunCompartmentRequest = ChangeJobRunCompartmentRequest
                .builder()
                .jobRunId(jobRunUUID)
                .changeJobRunCompartmentDetails(changeJobRunCompartmentDetails)
                .build();

        return clientDataScience.changeJobRunCompartment(changeJobRunCompartmentRequest);
    }

    public CancelJobRunResponse cancelJobRun(String jobRunUUID) {
        CancelJobRunRequest cancelJobRunRequest = CancelJobRunRequest.builder().jobRunId(jobRunUUID).build();
        return clientDataScience.cancelJobRun(cancelJobRunRequest);
    }

    public ListJobRunsResponse listJobRuns(String compartmentUuid) {
        //
        ListJobRunsRequest listJobRunsRequest =
                ListJobRunsRequest.builder()
                        .compartmentId(compartmentUuid)
                        .build();
        return clientDataScience.listJobRuns(listJobRunsRequest);
    }

    public List<JobRunSummary> listJobRunsByState(DataScienceClient clientDataScience, String compartmentUuid) {
        //
        ListJobRunsRequest listJobRunsRequest =
                ListJobRunsRequest.builder()
                        .compartmentId(compartmentUuid)
                        .lifecycleState(JobRunLifecycleState.Failed)
                        .build();
        List<JobRunSummary> jobRunsByState = clientDataScience.listJobRuns(listJobRunsRequest).getItems();

        return jobRunsByState;
    }

    public DeleteJobResponse deleteJob(String jobUuid) {
        return clientDataScience.deleteJob(
                DeleteJobRequest.builder()
                        .jobId(jobUuid)
                        .deleteRelatedJobRuns(true)
                        .build());
    }

    public DeleteJobRunResponse deleteJobRun(String jobRunUuid) {
        return clientDataScience.deleteJobRun(
                DeleteJobRunRequest
                        .builder()
                        .jobRunId(jobRunUuid)
                        .build());
    }

    public void monitorJobRun(String jobRunUuid) {
        while (true) {
            try {
                GetJobRunRequest getJobRunRequest =
                        GetJobRunRequest.builder().jobRunId(jobRunUuid).build();

                GetJobRunResponse getJobRunResponse = clientDataScience.getJobRun(getJobRunRequest);

                if (getJobRunResponse
                        .getJobRun()
                        .getLifecycleState()
                        .getValue()
                        .equalsIgnoreCase("IN_PROGRESS")
                        || getJobRunResponse
                        .getJobRun()
                        .getLifecycleState()
                        .getValue()
                        .equalsIgnoreCase("ACCEPTED")) {

                    System.out.println("-----");
                    System.out.println("NAME: " + getJobRunResponse.getJobRun().getDisplayName());
                    System.out.println("STATE: " + getJobRunResponse.getJobRun().getLifecycleState());
                    System.out.println("DETAILS: " + getJobRunResponse.getJobRun().getLifecycleDetails());
                    System.out.println(
                            " /ACCEPTED: " + getJobRunResponse.getJobRun().getTimeAccepted()
                                    + " /Artifact Run Started: " + getJobRunResponse.getJobRun().getTimeStarted() +
                                    " /FINISHED: " + getJobRunResponse.getJobRun().getTimeFinished());
                    System.out.println("-----");
                    Thread.sleep(5000);
                    continue;
                } else {
                    System.out.println("NAME: " + getJobRunResponse.getJobRun().getDisplayName());
                    System.out.println("STATE: " + getJobRunResponse.getJobRun().getLifecycleState());
                    System.out.println("DETAILS: " + getJobRunResponse.getJobRun().getLifecycleDetails());
                    System.out.println("STARTED: " + getJobRunResponse.getJobRun().getTimeStarted() + " /ACCEPTED: "
                            + getJobRunResponse.getJobRun().getTimeAccepted()
                            + " /FINISHED: " + getJobRunResponse.getJobRun().getTimeFinished());
                    break;
                }
            } catch (InterruptedException e) {
                System.err.println(e);
            }
        }
    }
}
