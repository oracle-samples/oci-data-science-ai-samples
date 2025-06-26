import oci
import os
import logging

def get_auth():
    PROFILE_NAME = 'DEFAULT'
    SECURITY_TOKEN_FILE_KEY = 'security_token_file'
    KEY_FILE_KEY = 'key_file'
    config = oci.config.from_file(profile_name=PROFILE_NAME)
    token_file = config[SECURITY_TOKEN_FILE_KEY]
    token = None
    with open(token_file, 'r') as f:
      token = f.read()
    private_key = oci.signer.load_private_key_from_file(config[KEY_FILE_KEY])
    signer = oci.auth.signers.SecurityTokenSigner(token, private_key) 
    return signer

def get_datascience_client():
    logger.info("Getting Resource Principal authenticated in datascience client")
    return oci.data_science.DataScienceClient({}, signer=get_auth(), service_endpoint=service_endpoint)

# Set up logging
_logger_name = 'MD'
logger = logging.getLogger(_logger_name)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', '%Y-%m-%d %H:%M:%S')
ch.setFormatter(formatter)
logger.addHandler(ch)


service_endpoint = "https://datascience.us-ashburn-1.oci.oraclecloud.com"

compartment_id = os.getenv('COMPARTMENT_ID', None)
project_id = os.getenv('PROJECT_ID', None)

logger.info("Setting up data-science client")
data_science_client = get_datascience_client()
logger.info("Data-science client set up successfully")

data_science_client.create_model_deployment(create_model_deployment_details = {
    "displayName": "streamable-mcp-redis",
    "projectId": project_id,
    "compartmentId": compartment_id,
    "modelDeploymentConfigurationDetails": {
        "deploymentType": "SINGLE_MODEL",
        "modelConfigurationDetails": {
            "modelId": <MODEL_ID>,
            "instanceConfiguration": {
                "instanceShapeName": "VM.Standard.E4.Flex",
                "modelDeploymentInstanceShapeConfigDetails": {
                    "ocpus": 1.0,
                    "memoryInGBs": 16.0,
                    "cpuBaseline": null
                },
                "subnetId": null,
                "privateEndpointId": null
            },
            "scalingPolicy": {
                "policyType": "FIXED_SIZE",
                "instanceCount": 1
            },
            "bandwidthMbps": 10,
            "maximumBandwidthMbps": 10
        },
        "streamConfigurationDetails": {
            "inputStreamIds": null,
            "outputStreamIds": null
        },
        "environmentConfigurationDetails": {
            "environmentConfigurationType": "OCIR_CONTAINER",
            "image": <CONTAINER_ID>, # example "iad.ocir.io/ociodscdev/mcp-sse-app:2.0.0"
            "imageDigest": <DIGEST>, # example "sha256:9cb77e0e2f53ec4198dadfc065c7b8358e24f41d3............",
            "cmd": null,
            "entrypoint": null,
            "serverPort": 8000,
            "healthCheckPort": 8000,
            "environmentVariables": {
                "WEB_CONCURRENCY": "1",
                "MODEL_DEPLOY_PREDICT_ENDPOINT": "/mcp/"
            }
        }
    },
    "categoryLogDetails": {
        "access": {
            "logId": <LOG_GROUP_ID>,
            "logGroupId": <LOG_ID>
        },
        "predict": {
            "logId": <LOG_GROUP_ID>,
            "logGroupId": <LOG_ID>
        }
    },
   "freeformTags": {},
    "definedTags": {}
})







