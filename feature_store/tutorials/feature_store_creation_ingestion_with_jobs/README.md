Feature Store Creation and Ingestion using ML Job
=====================

In this Example, you use the Oracle Cloud Infrastructure (OCI) Data Science service MLJob component to create OCI Feature store design time constructs and then ingest feature values into the offline feature store.

Tutorial picks use case of Electronic Heath Data consisting of Patient Test Results. The example demonstrates creation of feature store, entity , transformation and feature group design time constructs using a python script which is provided as job artifact. Another job artifact demonstrates ingestion of feature values into pre-created feature group.

## Prerequisites

The notebook makes connections to other OCI resources. This is done using [resource principals](https://docs.oracle.com/en-us/iaas/Content/Functions/Tasks/functionsaccessingociresources.htm). If you have not configured your tenancy to use resource principals then you can do so using the instructions that are [here](https://docs.oracle.com/en-us/iaas/data-science/using/create-dynamic-groups.htm). Alternatively, you can use API keys. The preferred method for authentication is resource principals.


## Instructions using programmatic interface

1. Open a Data Science Notebook session (i.e. JupyterLab).
2. Open a file terminal by clicking on File -> New -> Terminal.
3. In the terminal run the following commands:
4. `odsc conda install -s fspyspark32_p38_cpu_v{version}` to install the feature store conda.
    1. `conda activate /home/datascience/conda/fspyspark32_p38_cpu_v{version}` to activate the conda.
5. Copy the `notebooks` folder into the notebook session.
6. Open the notebook `feature_store_using_mljob.ipynb`.
7. Change the notebook kernel to `Python [conda env:fspyspark32_p38_cpu_v{version}]`.
8. Read the notebook and execute each cell.
9. Once the ml job run is completed successfully, user can validate creation of feature store construct using the feature store notebook ui extension.
10. Now open the notebook `feature_store_ingestion_via_mljob.ipynb`.
11. Change the notebook kernel to `Python [conda env:fspyspark32_p38_cpu_v{version}]`.
12. Read the notebook and execute each cell.
13. validate the ingestion ml job is executed successfully.
14. User can validate the ingested data and other metadata using the feature store notebook ui extension.

## Instructions using YAML

1. Ensure that you have the ads command-line tool installed and configured properly.
2. Replace the placeholders in ```oci-datascience-template.yaml``` with your specific values for <name>, <compartment_id>, <mybucket>, <mynamespace> and <path_to_conda_pack>.
3. Open your terminal and navigate to the directory containing ```oci-datascience-template.yaml```.
   ```yaml
   kind: job
   name: "{Job name.}"
   spec:
     infrastructure:
       kind: infrastructure
       spec:
         blockStorageSize: 50
         subnetId: ocid1.subnet.oc1.iad..<unique_ID>
         compartmentId: ocid1.compartment.oc1..<unique_ID>
         projectId: ocid1.datascienceproject.oc1.iad..<unique_ID>
         logGroupId: ocid1.loggroup.oc1.iad..<unique_ID>
         logId: ocid1.log.oc1.iad..<unique_ID>
         shapeName: VM.Standard.E3.Flex
         shapeConfigDetails:
           memoryInGBs: 20
           ocpus: 2
         jobInfrastructureType: ME_STANDALONE
         jobType: DEFAULT
       type: dataScienceJob
     runtime:
       kind: runtime
       spec:
         args: []
         conda:
           type: published
           uri: oci://bucket@namespace/prefix
         env:
         - name: TEST
           value: TEST_VALUE
         entrypoint: "{Entry point script.}"
         scriptPathURI: "{Path to the script.}"
       type: python
   ```
4. Run the following command:
   ```bash
   ads opctl run -f oci-datascience-template.yaml
   ```
5. This command will trigger the execution of the ML job defined in the oci-datascience-template.yaml configuration file. Ensure that all placeholders are replaced with appropriate values before running the command.
6. Check the progress of the training by running in the Notebook Terminal:
   ```bash
   ads opctl watch <job run ocid of job-run-ocid>
   ```
