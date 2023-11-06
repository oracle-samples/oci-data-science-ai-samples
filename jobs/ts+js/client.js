const odcs = require("oci-datascience");
const common = require("oci-common");
const fs = require('fs')

// TODO: Replace these with your tenancy OCIDs!
const tenancy = {
    projectId: process.env.PROJECT,
    compartmentId: process.env.COMPARTMENT,
    // subnetId: process.env.SUBNET,
    logGroupId: process.env.LOGGROUP,
    tenancyName: process.env.TENANCY,
    config: process.env.CONFIG
}

const provider = new common.ConfigFileAuthenticationDetailsProvider(tenancy.config, tenancy.tenancyName);

// Init Data Science Client
let client = new odcs.DataScienceClient({
    authenticationDetailsProvider: provider
})

async function listJobShapes(compartmentId) {
    const listJobShapesRequest = {
        compartmentId: compartmentId
    };

    const shapes = await client.listJobShapes(listJobShapesRequest);
    console.log(shapes);
}

async function createJob(name, projectId, compartmentId, log_group_id, subnet_id) {
    const createJobRequest = {
        createJobDetails: {
            projectId: projectId,
            compartmentId: compartmentId,
            displayName: name,
            description: "Not mandatory description",
            jobConfigurationDetails: {
                jobType: "DEFAULT",
                environmentVariables: {
                    CONDA_ENV_TYPE: "service",
                    CONDA_ENV_SLUG: "generalml_p38_cpu_v1"
                },
            },
            jobInfrastructureConfigurationDetails: {
                jobInfrastructureType: "ME_STANDALONE", //STANDALONE
                shapeName: "VM.Standard2.1",
                blockStorageSizeInGBs: "100",
                // required if jobInfrastructureType: "STANDALONE"
                // subnetId: subnet_id,
            },
            // not mandatory
            jobLogConfigurationDetails: {
                enableLogging: true,
                enableAutoLogCreation: false,
                logGroupId: log_group_id
            }
        }
    };

    return client.createJob(createJobRequest);
}

async function getJob(jobId) {
    const getJobRequest = {
        jobId: jobId
    }
    return client.getJob(getJobRequest);
}

async function updateJob(jobId, name) {
    const updateJobRequest = {
        jobId: jobId,
        updateJobDetails: {
            displayName: name,
            description: "No mandatory update description",
            jobInfrastructureConfigurationDetails: {
                jobInfrastructureType: "ME_STANDALONE",
                shapeName: "VM.Standard2.1",
                blockStorageSizeInGBs: "101",
            },
        }
    }
    return client.updateJob(updateJobRequest);
}

async function listJobs(projectId, compartmentId) {
    const listJobsRequest = {
        projectId: projectId,
        compartmentId: compartmentId,
        // Optional 
        // displayName: ,
        // lifecycleState: ,
        // createdBy: ,
        // limit: ,
        // page: ,
        // sortOrder: ,
        // sortBy: 
    }

    return client.listJobs(listJobsRequest);
}

// Notice this example does not use chunks for large files!
async function createJobArtifact(jobId, filename) {
    const data = fs.readFileSync(filename, 'utf8');

    const createJobArtifactRequest = {
        jobId: jobId,
        contentDisposition: "attachment; filename=" + filename,
        jobArtifact: data
    }
    return client.createJobArtifact(createJobArtifactRequest);
}

async function headJobArtifact(jobId) {
    const headJobArtifactRequest = {
        jobId: jobId
    }

    return client.headJobArtifact(headJobArtifactRequest);
}

async function getJobArtifact(jobId) {
    const getJobArtifactRequest = {
        jobId: jobId
    }
    let filedata = await client.getJobArtifactContent(getJobArtifactRequest);

    // only if job artifact exist
    if (filedata && filedata.contentDisposition) {
        let regexJobArtifactName = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/;
        let matches = regexJobArtifactName.exec(filedata.contentDisposition);
        let jobArtifactName = undefined;

        if (matches != null && matches[1]) {
            jobArtifactName = matches[1].replace(/['"]/g, '');
        }

        if (jobArtifactName) {
            let download_stream = await fs.createWriteStream(jobArtifactName);
            const stream = new WritableStream({
                write(chunk) {
                    download_stream.write(chunk);
                },
            });
            filedata.value.pipeTo(stream)
        }
    }
    return "DONE";
}

async function changeJobCompartment(jobId, changeToCompartmentId) {
    const changeJobCompartmentRequest = {
        jobId: jobId,
        changeJobCompartmentDetails: {
            compartmentId: changeToCompartmentId
        }
    }
    return client.changeJobCompartment(changeJobCompartmentRequest);
}

async function createJobRun(projectId, compartmentId, jobId, name) {
    const createJobRunRequest = {
        createJobRunDetails: {
            projectId: projectId,
            compartmentId: compartmentId,
            jobId: jobId,
            displayName: name,
            jobConfigurationOverrideDetails: {
                jobType: "DEFAULT",
                environmentVariables: {
                    CONDA_ENV_TYPE: "service",
                    CONDA_ENV_SLUG: "generalml_p38_cpu_v1",
                }
            },
            jobLogConfigurationOverrideDetails: {
                enableLogging: true,
                enableAutoLogCreation: true,
            },
        }
    }

    return client.createJobRun(createJobRunRequest);
}

async function getJobRun(jobRunId) {
    const getJobRunRequest = {
        jobRunId: jobRunId
    }
    return client.getJobRun(getJobRunRequest);
}

async function listJobRuns(jobId, compartmentId) {
    const listJobRunsRequest = {
        jobId: jobId,
        compartmentId: compartmentId,
        // Optional 
        // createdBy: ,
        // displayName: ,
        // limit: ,
        // page: ,
        // sortOrder: ,
        // sortBy: ,
        // lifecycleState: 
    }

    return client.listJobRuns(listJobRunsRequest);
}

async function updateJobRuns(jobRunId) {
    const updateJobRunRequest = {
        jobRunId: jobRunId,
        updateJobRunDetails: {
            displayName: "Job Run NodeJS Updated Name",
            freeformTags: { key1: "lvp" },
        }
    }

    return await client.updateJobRun(updateJobRunRequest);
}

async function changeJobRunCompartment(jobRunId, changeToCompartmentId) {
    const changeJobRunCompartmentRequest = {
        jobRunId: jobRunId,
        changeJobRunCompartmentDetails: {
            compartmentId: changeToCompartmentId
        }
    }
    return client.changeJobRunCompartment(changeJobRunCompartmentRequest);
}

async function cancelJobRun(jobRunId) {
    const cancelJobRunRequest = {
        jobRunId: jobRunId
    }

    return client.cancelJobRun(cancelJobRunRequest);
}

(async () => {
    // current date-time
    const datetime = Date.now();

    const jobShapes = await listJobShapes(tenancy.compartmentId);
    console.log(jobShapes)

    const createJobResponse = await createJob(
        "Job NodeJS Test " + datetime,
        tenancy.projectId,
        tenancy.compartmentId,
        tenancy.logGroupId
        // tenancy.subnetId
    )
    console.log(createJobResponse);

    console.log("Get Job Details")
    const getJobDetails = await getJob(createJobResponse.job.id);
    console.log(getJobDetails);

    console.log("updateJob")
    const updatedJobResponse = await updateJob(createJobResponse.job.id, "Node Job Update " + datetime);
    console.log(updatedJobResponse);

    console.log("listJobs")
    const listAllJobs = await listJobs(tenancy.projectId, tenancy.compartmentId);
    console.log(listAllJobs);

    console.log("createJobArtifact");
    const createArtifactResponse = await createJobArtifact(createJobResponse.job.id, "hello_world_job.py");
    console.log(createArtifactResponse);

    console.log("headJobArtifact");
    const headJobArtifactResponse = await headJobArtifact(createJobResponse.job.id);
    console.log(headJobArtifactResponse);

    console.log("getJobArtifact");
    console.log(await getJobArtifact(createJobResponse.job.id));

    console.log("createJobRun");
    const jobRunRespone = await createJobRun(tenancy.projectId, tenancy.compartmentId, createJobResponse.job.id, "Node Job Run");
    console.log("JobRunID: " + jobRunRespone.jobRun.id);

    console.log("getJobRun");
    let getJobRunResponse = await getJobRun(jobRunRespone.jobRun.id);
    console.log(getJobRunResponse.jobRun.id);

    console.log("listJobRuns");
    let listJobRunsResponse = await listJobRuns(createJobResponse.job.id, tenancy.compartmentId);
    console.log(listJobRunsResponse);

    console.log("updateJobRuns");
    let updateJobRunsResponse = await updateJobRuns(getJobRunResponse.jobRun.id);
    console.log(updateJobRunsResponse);

    // You can't cancel Job Run in ACCEPTED, CANCELLING, DELETED or NEEDS_ATTENTION state

    // console.log("cancelJobRun");
    // let cancelJobRunRequest = await cancelJobRun(getJobRunResponse.jobRun.id);
    // console.log(cancelJobRunRequest);

})();