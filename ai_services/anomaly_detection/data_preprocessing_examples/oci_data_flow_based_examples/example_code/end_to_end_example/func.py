import io
import oci
import json

from fdk import response

signer = oci.auth.signers.get_resource_principals_signer()
object_storage_client = oci.object_storage.ObjectStorageClient(config={}, signer=signer)
data_flow_client = oci.data_flow.DataFlowClient(config={}, signer=signer)

def handler(ctx, data: io.BytesIO=None):
    try:
        body = json.loads(data.getvalue())
        bucketName = body["data"]["additionalDetails"]["bucketName"]
        namespace = body["data"]["additionalDetails"]["namespace"]
        objectName = body["data"]["resourceName"]
    except Exception:
        error = 'Input a JSON object in the format: \'{"bucketName": "<bucket name>"}, "objectName": "<object name>"}\' '
        raise Exception(error)
    config_bucket_name = "placeholder"
    object_name = "placeholder"
    if bucketName == "raw-data-bucket":
        config_bucket_name = "training-config-bucket"
        object_name = "driver-demoable-complete-v2.json"
        resp = get_object(namespace, config_bucket_name, object_name)
        call_dataflow(resp, "applyAndFinalize")
    elif bucketName == "inferencing-data-bucket":
        config_bucket_name = "inferencing-config-bucket"
        object_name = "driver-demoable-complete-v2.json"
        resp = get_object(namespace, config_bucket_name, object_name)
        call_dataflow(resp, "apply")

def get_object(namespace, bucket, file):
    get_resp = object_storage_client.get_object(namespace, bucket, file)
    assert get_resp.status in [
        200,
        201,
    ], f"Unable to get object from {bucket}@{namespace}! Response: {get_resp.text}"
    return get_resp.data.text

def call_dataflow(response, phase):
    create_run_response = data_flow_client.create_run(
        create_run_details=oci.data_flow.models.CreateRunDetails(
            compartment_id="ocid1.compartment.oc1..aaaaaaaa26brugmo3vvh7tjtyew5pbclnd4i4m2pr7kt2ho7db4gdlzekmha",
            application_id="ocid1.dataflowapplication.oc1.phx.anyhqljtor7l3jiawefbhoanxrutylds32jpyozmtjrxcjjji4jnv5ztccla",
            arguments=[ "--response", response, "--phase", phase],
            display_name="complete-dpp-test",
            logs_bucket_uri="oci://logs-bucket@ax3dvjxgkemg/")
    )

    return { "content": create_run_response }