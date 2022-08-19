import io
import os
import json
import sys
from fdk import response

import oci.object_storage
import oci.data_flow

signer = oci.auth.signers.get_resource_principals_signer()
os_client = oci.object_storage.ObjectStorageClient(config={}, signer=signer)
data_flow_client = oci.data_flow.DataFlowClient(config={}, signer=signer)

def handler(ctx, data: io.BytesIO=None):
    try:
        body = json.loads(data.getvalue())
        bucketName = body["data"]["additionalDetails"]["bucketName"]
        objectName = body["data"]["resourceName"]
    except Exception:
        error = 'Input a JSON object in the format: \'{"bucketName": "<bucket name>"}, "objectName": "<object name>"}\' '
        raise Exception(error)
    try:
        get_resp = get_object(bucketName, objectName)
        contents = json.loads(get_resp)
        input_csv = contents["inputCSV"]
        columns_to_remove = contents["columnsToRemove"]
        output = contents["outputPath"]

        df_response = call_dataflow(input_csv, columns_to_remove, output)
        # print(str(df_response))

    except Exception as e:
        raise Exception(e)
    
    return response.Response(
        ctx,
        response_data=df_response,
        headers={"Content-Type": "application/json"}
    )

def get_object(bucketName, objectName):
    namespace = os_client.get_namespace().data
    try:
        print("Searching for bucket and object", flush=True)
        object = os_client.get_object(namespace, bucketName, objectName)
        print("found object", flush=True)
        if object.status == 200:
            print("Success: The object " + objectName + " was retrieved with the content: " + object.data.text, flush=True)
            message = object.data.text
        else:
            message = "Failed: The object " + objectName + " could not be retrieved."
    except Exception as e:
        message = "Failed: " + str(e.message)
    return message

def call_dataflow(input_csv, columns_to_remove, output):
    create_run_response = data_flow_client.create_run(
        create_run_details=oci.data_flow.models.CreateRunDetails(
            compartment_id="<compartment-ocid>",
            application_id="<application-ocid>",
            arguments=[ "--input", input_csv, "--columns_to_remove", columns_to_remove, "--output", output],
            display_name="<display-name-you-like>",
            logs_bucket_uri="oci://<bucket-name>@<namespace>/")
    )

    return { "content": create_run_response }