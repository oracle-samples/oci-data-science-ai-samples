const odcs = require("oci-datascience");
const common = require("oci-common");

const tenancy = {
    projectId: process.env.PROJECT,
    compartmentId: process.env.COMPARTMENT,
    // subnetId: process.env.SUBNET,
    logGroupId: process.env.LOGGROUP,
    tenancyName: process.env.TENANCY,
    config: process.env.CONFIG
}

const provider = new common.ConfigFileAuthenticationDetailsProvider(tenancy.config, tenancy.tenancyName);

let client = new odcs.DataScienceClient({
    authenticationDetailsProvider: provider
})

async function deleteJobRun(jobRunId) {
    const deleteJobRunRequest = {
        jobRunId: jobRunId
    }
    return client.deleteJobRun(deleteJobRunRequest);
}

async function deleteJob(jobId, deleteRelatedJobRuns = false) {
    const deleteJobRequest = {
        jobId: jobId,
        deleteRelatedJobRuns: deleteRelatedJobRuns
    }
    return client.deleteJob(deleteJobRequest);
}


(async () => {
    // NOTICE: You cannot delete JobRun or Job during the Cancel or Running lifecycle!

    console.log("deleteJobRun");
    let deleteJobRunRequest = await deleteJobRun("<JobRun OCID>");
    console.log(deleteJobRunRequest);

    console.log("deleteJob");
    let deleteJobRequest = await deleteJob("<JobRun OCID>", true);
    console.log(deleteJobRequest);
})();