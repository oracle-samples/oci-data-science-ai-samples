Feature Store Creation and Ingestion using Data Flow
=====================================================

In this Example, you use the Oracle Cloud Infrastructure (OCI) Data Flow Run to create OCI Feature store design time constructs and then ingest feature values into the offline feature store.

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
6. Open the notebook `feature_store_via_dataflow.ipynb`.
7. Change the notebook kernel to `Python [conda env:fspyspark32_p38_cpu_v{version}]`.
8. Read the notebook and execute each cell.
9. Once the data flow run is completed successfully, user can validate creation of feature store construct using the feature store notebook ui extension.
10. Now open the notebook `feature_store_ingestion_via_dataflow.ipynb`.
11. Change the notebook kernel to `Python [conda env:fspyspark32_p38_cpu_v{version}]`.
12. Read the notebook and execute each cell.
13. validate the ingestion data flow job is executed successfully.
14. User can validate the ingested data and other metadata using the feature store notebook ui extension.

## Instructions using YAML

Follow these steps to execute the defined job configuration:

1. Ensure that you have the ads command-line tool installed and configured properly.
2. Replace the placeholders in ```oci-datascience-template.yaml``` with your specific values for <uuid>, <compartment_id>, <mybucket>, <mynamespace>, <dataflow-logs-prefix>, <subdir_to_put_and_get_script>, and <path_to_conda_pack>.
3. Open your terminal and navigate to the directory containing ```oci-datascience-template.yaml```.
   ```yaml
   kind: job
   name: "{DataFlow application name}"
   spec:
     infrastructure:
       kind: infrastructure
       spec:
         compartmentId: ocid1.compartment.oc1..<unique_ID>
         driverShape: VM.Standard.E4.Flex
         driverShapeConfig:
           memory_in_gbs: 32
           ocpus: 2
         executorShape: VM.Standard.E4.Flex
         executorShapeConfig:
           memory_in_gbs: 32
           ocpus: 2
         language: PYTHON
         logsBucketUri: oci://bucket@namespace/
         numExecutors: 1
         sparkVersion: 3.2.1
         privateEndpointId: ocid1.dataflowprivateendpoint.oc1..<unique_ID>
       type: dataFlow
     runtime:
       kind: runtime
       spec:
         configuration:
           spark.driver.memory: "16G"
         conda:
           type: published
           uri: oci://bucket@namespace/prefix
         condaAuthType: resource_principal
         scriptBucket: oci://bucket@namespace/dataflow/script
         scriptPathURI: "feature_store_creation.py"
         overwrite: True
       type: dataFlow
   ```
4. Run the following command:
   ```bash
   ads jobs run -f oci-datascience-template.yaml
   ```
5. This command will trigger the execution of the Data Flow job defined in the oci-datascience-template.yaml configuration file. Ensure that all placeholders are replaced with appropriate values before running the command.
