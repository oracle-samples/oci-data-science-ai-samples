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
    "displayName": "Diffusion Model deployment",
    "projectId": project_id,
    "compartmentId": compartment_id,
    "modelDeploymentConfigurationDetails": {
        "deploymentType": "SINGLE_MODEL",
        "modelConfigurationDetails": {
            "modelId": <MODEL_ID>,
            "instanceConfiguration": {
                "instanceShapeName": "VM.GPU.A10.2",
                "modelDeploymentInstanceShapeConfigDetails": None,
                "subnetId": "<SUBNET_ID>",
                "privateEndpointId": None
            },
            "scalingPolicy": {
                "policyType": "FIXED_SIZE",
                "instanceCount": 1
            },
            "bandwidthMbps": 10,
            "maximumBandwidthMbps": 10
        },
        "streamConfigurationDetails": {
            "inputStreamIds": None,
            "outputStreamIds": None
        },
        "environmentConfigurationDetails": {
            "environmentConfigurationType": "OCIR_CONTAINER",
            "image": <CONTAINER_ID>, 
            "imageDigest": <DIGEST>, 
            "cmd": None,
            "entrypoint": None,
            "serverPort": 3000,
            "healthCheckPort": 3000,
            "environmentConfigurationDetails": {
              "environmentConfigurationType": "OCIR_CONTAINER",
              "image": "<IMAGE_ID>",
              "imageDigest": "<DIGEST>",
              "cmd": None,
              "entrypoint": None,
              "serverPort": 3000,
              "healthCheckPort": 3000,
              "environmentVariables": {
                  "MODEL_DEPLOY_HEALTH_ENDPOINT": "/readyz",
                  "SHM_SIZE": "10g",
                  "HF_TOKEN": "<HF_TOKEN_FOR_MODEL_DOWNLOAD>" # No need if using cataloged model
            }
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
