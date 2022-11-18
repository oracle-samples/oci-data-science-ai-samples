import argparse
import json
import logging
import sys
import oci
import oci.data_science as data_science
from oci.data_science.models import CreateModelDeploymentDetails, ModelConfigurationDetails
from oci.data_science.models import InstanceConfiguration, FixedSizeScalingPolicy
from oci.data_science.models import CategoryLogDetails, LogDetails

# Deployment SDK
from oci.signer import Signer
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger("Model Deployment Example")

class ModelDeployment:
    def __init__(self, oci_config_file):
        self.model_deployment_id = None
        self.config_file = oci_config_file
        fp = open('model_deployment_config.json')
        general_data = json.load(fp)
        self.project_id = general_data['project_id']
        self.compartment_id = general_data['compartment_id']
        self.deployment_name = general_data['deployment_name']
        self.model_id = general_data['model_id']
        self.instance_shape_name = general_data['instance_shape_name']
        self.instance_count = int(general_data['instance_count'])
        self.bandwidth_mbps = int(general_data['bandwidth_mbps'])
        self.access_log_id = general_data['access_log_id']
        self.predict_log_id = general_data['predict_log_id']
        self.log_group_id = general_data['log_group_id']
        self.active = False
        if not (self.project_id and self.compartment_id and self.model_id):
            fp.close()
            logger.error(f'Model artifact deployment failed. Invalid json file')
            return
        # -- Create data science client and data science composite client with oci config to organize your work
        try:
            # read oci_config file
            self.oci_config = oci.config.from_file(self.config_file, "DEFAULT")
            self.data_science_client = data_science.DataScienceClient(config=self.oci_config)
            self.data_science_composite_client = data_science.DataScienceClientCompositeOperations(self.data_science_client)
            self.auth = Signer(tenancy=self.oci_config['tenancy'], user=self.oci_config['user'], fingerprint=self.oci_config['fingerprint'], private_key_file_location=self.oci_config['key_file'], pass_phrase=self.oci_config['pass_phrase'])
        except Exception as e:
            raise e

    def create_model_deployment(self):
        # -- Create a model deployment
        logger.info(f"Starting to create a model deployment")
        try:
            self.instance_configuration = InstanceConfiguration()  # model deployment instance configuration
            self.instance_configuration.instance_shape_name = self.instance_shape_name
            self.scaling_policy = FixedSizeScalingPolicy()  # the fixed size scaling policy for model deployment
            self.scaling_policy.instance_count = self.instance_count
            # create a model confifguration details object
            model_config_details = ModelConfigurationDetails(model_id=self.model_id, bandwidth_mbps=self.bandwidth_mbps, instance_configuration=self.instance_configuration, scaling_policy=self.scaling_policy)
            # create a model type deployment
            single_model_deployment_config_details = data_science.models.SingleModelDeploymentConfigurationDetails(deployment_type="SINGLE_MODEL", model_configuration_details=model_config_details)
            # set up parameters required to create a new model deployment.
            create_model_deployment_details = CreateModelDeploymentDetails(display_name=self.deployment_name, model_deployment_configuration_details=single_model_deployment_config_details, compartment_id=self.compartment_id, project_id=self.project_id)
            # if log info is provided in model_deployment_config.json file
            if self.log_group_id and (self.predict_log_id or self.access_log_id):
                create_model_deployment_details.category_log_details = self.create_logging(self.log_group_id, self.access_log_id, self.predict_log_id)
            # create a model deployment with data science composite client
            create_model_deployment_response = self.data_science_composite_client.create_model_deployment_and_wait_for_state(create_model_deployment_details=create_model_deployment_details, wait_for_states=["SUCCEEDED", "FAILED"])
            work_request_resources = create_model_deployment_response.data.resources
            self.model_deployment_id = work_request_resources[0].identifier
            if create_model_deployment_response.data.status == "SUCCEEDED":
                logger.info(f"Created a model deployment.")
                self.active = True
            else:
                logger.error(f"Failed to create a model deployment.")
        except Exception as e:
            logger.error(f"Failed to create a model deployment.")
            raise e

    def write_model_deployment_info(self):
        # -- write model deployment id and url into model_deployment_config.json file
        try:
            model_deployment = self.data_science_client.get_model_deployment(model_deployment_id=self.model_deployment_id)
            with open('model_deployment_config.json', 'r+') as f:
                data = json.load(f)
                data['model_deployment_url'] = model_deployment.data.model_deployment_url
                data['model_deployment_id'] = model_deployment.data.id
                f.seek(0)
                json.dump(data, f, indent=4)
                logger.info(f"Model deployment info written to model_deployment_config.json file")
                logger.info(f"Model Deployment ID: %s", model_deployment.data.id )
                logger.info(f"Model Deployment url: %s", model_deployment.data.model_deployment_url)
        except Exception as e:
            logger.error("Failed to write model deployment info to model_deployment_config.json file.")
            raise e

    def create_logging(self, log_group_id, access_log_id, predict_log_id):
        try:
            category_log_details = CategoryLogDetails()
            if access_log_id:
                access_log_details = LogDetails()
                access_log_details.log_id = access_log_id
                access_log_details.log_group_id = log_group_id
                category_log_details.access = access_log_details
            if predict_log_id:
                predict_log_details = LogDetails()
                predict_log_details.log_id = predict_log_id
                predict_log_details.log_group_id = log_group_id
                category_log_details.predict = predict_log_details
            return category_log_details
        except Exception as e:
            logger.error("Failed to create logs.")
            raise e

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Deploy A Model")
    parser.add_argument("--oci_config_file", nargs="?", help="Config file containing OCID's", default="~/.oci/config")
    args = parser.parse_args()
    try:
        md = ModelDeployment(args.oci_config_file)  # initialize a model deployment
        md.create_model_deployment()  # create a model deployment
        md.write_model_deployment_info()  # write a model deployment into model_deployment_config.json
    except Exception as e:
        logger.error(e)
