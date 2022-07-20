import argparse
import logging
import sys
import oci
import json

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger("Model Deployment Example")

def delete_model(config_name):
    try:
        # read oci config
        oci_config = oci.config.from_file(config_name, "DEFAULT")
        ds_client = oci.data_science.DataScienceClient(config=oci_config)
        fp = open('model_deployment_config.json')
        data = json.load(fp)
        model_ocid = data["model_id"]
        logger.info(f'Starting to delete model artifact')
        ds_client.delete_model(model_ocid)
        logger.info(f'Finished deleting model artifact')
        fp.close()
    except Exception as e:
        raise e

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Deleting model artifact")
    parser.add_argument("--oci_config_file", nargs="?", help="Config file containing OCID's", default="~/.oci/config")
    args = parser.parse_args()
    delete_model(args.oci_config_file)