Feature Store Creation and Ingestion using ML Job
=====================

In this Example, you use the Oracle Cloud Infrastructure (OCI) Data Science service MLJob component to create OCI Feature store design time constructs and then ingest feature values into the offline feature store.

Tutorial picks use case of Electronic Heath Data consisting of Patient Test Results. The example demonstrates creation of feature store, entity , transformation and feature group design time constructs using a python script which is provided as job artifact. Another job artifact demonstrates ingestion of feature values into pre-created feature group.

# Prerequisites

The notebook makes connections to other OCI resources. This is done using [resource principals](https://docs.oracle.com/en-us/iaas/Content/Functions/Tasks/functionsaccessingociresources.htm). If you have not configured your tenancy to use resource principals then you can do so using the instructions that are [here](https://docs.oracle.com/en-us/iaas/data-science/using/create-dynamic-groups.htm). Alternatively, you can use API keys. The preferred method for authentication is resource principals.


# Instructions

1. Open a Data Science Notebook session (i.e. JupyterLab).
2. Open a file terminal by clicking on File -> New -> Terminal.
3. In the terminal run the following commands:
4. `odsc conda install -s fspyspark32_p38_cpu_v{version}` to install the feature store conda.
    1. `conda activate /home/datascience/conda/fspyspark32_p38_cpu_v{version}` to activate the conda.
5. Copy the `notebooks` folder into the notebook session.
6. Open the notebook `notebook/feature_store_using_mljob.ipynb`.
7. Change the notebook kernel to `Python [conda env:fspyspark32_p38_cpu_v{version}]`.
8. Read the notebook and execute each cell.
9. Once the ml job run is completed successfully, user can validate creation of feature store construct using the feature store notebook ui extension.
10. Now open the notebook `notebook/feature_store_ingestion_via_mljob.ipynb`.
11. Change the notebook kernel to `Python [conda env:fspyspark32_p38_cpu_v{version}]`.
12. Read the notebook and execute each cell.
13. validate the ingestion ml job is executed successfully.
14. User can validate the ingested data and other metadata using the feature store notebook ui extension.


