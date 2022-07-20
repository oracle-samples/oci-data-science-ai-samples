import argparse
import json
import logging
import sys
import oci
import oci.data_science as data_science

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger("Model Deployment Example")

class ModelDeployment:
    def __init__(self, oci_config_file):
        self.model_deployment_id = None
        self.config_file = oci_config_file
        # Get model deployment config info
        fp = open('model_deployment_config.json')
        general_data = json.load(fp)
        self.deployment_id = general_data['model_deployment_id']
        # -- Create data science client and data science composite client with oci config to organize your work
        try:
            # Read oci_config file
            self.oci_config = oci.config.from_file(self.config_file, "DEFAULT")
            self.data_science_client = data_science.DataScienceClient(
                config=self.oci_config
            )
            self.data_science_composite_client = data_science.DataScienceClientCompositeOperations(self.data_science_client)
        except Exception as e:
            raise e

    def remove_model_deployment(self):
        # -- Delete a model deployment
        logger.info(f'Deleting the model deployment.')
        try:
            delete_model_deployment_response = self.data_science_composite_client.delete_model_deployment_and_wait_for_state(
                self.deployment_id, wait_for_states=["SUCCEEDED", "FAILED"])
            if delete_model_deployment_response.data.status == "SUCCEEDED":
                logger.info(f"Deleted the model deployment, model_deployment_id = %s", self.deployment_id)
                self.model_deployment_id = None
            else:
                logger.error(f"Deleting the model deployment failed!!! ")
        except Exception as e:
            logger.error(f"Deleting the model deployment failed!!!")
            raise e


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Delete Model Deployment")
    parser.add_argument("--oci_config_file", nargs="?", help="Config file containing OCID's", default="~/.oci/config")
    args = parser.parse_args()
    try:
        md = ModelDeployment(args.oci_config_file)  # initialize a model deployment
        md.remove_model_deployment()  # delete a model deployment
    except Exception as e:
        logger.error(e)
