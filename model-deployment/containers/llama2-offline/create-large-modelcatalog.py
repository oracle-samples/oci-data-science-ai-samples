import oci
import time

# Get Data Science client
def get_datascience_client(resource_principal):
  if not resource_principal: 
    config = oci.config.from_file()
    return oci.data_science.DataScienceClient(config)
  else: 
    config = {}
    auth = oci.auth.signers.get_resource_principals_signer()
    return oci.data_science.DataScienceClient(config, signer=auth)

# Create Model
def create_model(data_science, model_display_name, compartment_id, project_id):
# Reference : https://docs.oracle.com/en-us/iaas/api/#/en/data-science/20190101/Model/CreateModel
# Required policies for export API to work:
  ## Allow service datascience to manage object-family in compartment <compartment> where ALL {target.bucket.name='<bucket_name>'}
	## Allow service objectstorage to manage object-family in compartment <compartment> where ALL {target.bucket.name='<bucket_name>'}
# For all data science releated policies, refer page: https://docs.oracle.com/en-us/iaas/data-science/using/policies.htm
  create_model_response = data_science.create_model(
    create_model_details=oci.data_science.models.CreateModelDetails(
      compartment_id=compartment_id,
      project_id=project_id,
      display_name=model_display_name
    )
  )
  # Get the data from response
  return create_model_response.data.id

# Export artifact to Model
def export_model_artifact(data_science, model_id, namespace, source_bucket, source_object_name, source_region):
# Reference : https://docs.oracle.com/en-us/iaas/api/#/en/data-science/20190101/Model/ExportModelArtifact
  export_model_artifact_response = data_science.export_model_artifact(
    model_id=model_id,
    export_model_artifact_details=oci.data_science.models.ExportModelArtifactDetails(
      artifact_export_details=oci.data_science.models.ArtifactExportDetailsObjectStorage(
          artifact_source_type="ORACLE_OBJECT_STORAGE",
          namespace=namespace,
          source_bucket=source_bucket,
          source_object_name=source_object_name,
          source_region=source_region
      )
    )
  )
  # Get the data from response
  return export_model_artifact_response

# Get upload artifact work request status for 1 hour or finished status
def get_upload_status(data_science, workRequestId):
  # Reference: https://docs.oracle.com/en-us/iaas/api/#/en/data-science/20190101/WorkRequest/GetWorkRequest
  exit = False
  # Sleep 30 seconds in between attempts
  sleepTimer = 30
  # Max 1 hour we will poll for work request. After this user can manually check with work request id.
  maxAttempts = 120
  attempts = 0
  get_work_request_response = {}
  while exit != True:
    print("Keep polling work request status every 30 seconds for an hour, for a concluding status. Interrupt process to exit.")
    get_work_request_response = data_science.get_work_request(
      work_request_id=workRequestId
    )
    attempts+=1
    print("Percentage completed: ", get_work_request_response.data.percent_complete)
    if (get_work_request_response.data.status != "ACCEPTED" and get_work_request_response.data.status != "IN_PROGRESS") or (attempts == maxAttempts):
      exit = True
      break
    time.sleep(sleepTimer)
  print("Completed with status: ", get_work_request_response.data.status)

if __name__ == '__main__':

  # Get user inputs
  ## Input for data science client creation
  resource_principal = False

  ## Add inputs for model creation
  compartmentId = <COMPARTMENT_OCID>
  project_id = <PROJECT_OCID>
  model_display_name = <OPTIONAL MODEL NAME>
 
  ## Add inputs for model export
  namespace = <BUCKET_NAMESPACE_HOSTING_MODEL_ZIP>
  source_bucket = <BUCKET_HOSTING_MODEL_ZIP>
  source_object_name = <MODEL_OBJECT_ZIP_NAME>
  source_region = <REGION_OF_BUCKET>
  
  # Get Client
  data_science = get_datascience_client(resource_principal)
  
  # Create Model
  model_id = create_model(data_science, model_display_name, compartmentId, project_id)

  # Attach artifact to model
  export_model_artifact_response = export_model_artifact(data_science, model_id, namespace, source_bucket, source_object_name, source_region)
  print(export_model_artifact_response.headers)

  # Get status of work request ID. Need data-science-work-requests policy for the principal
  # Example: allow group <group_name> to manage data-science-work-requests in compartment <compartment_name>
  # Refer page for more details: https://docs.oracle.com/en-us/iaas/data-science/using/policies.htm
  get_upload_status(data_science, export_model_artifact_response.headers["opc-work-request-id"])