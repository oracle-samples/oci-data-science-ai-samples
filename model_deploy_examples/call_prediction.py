import argparse
import base64
import json
import logging
import os
import sys
import traceback
import oci
import requests
import yaml
from oci.signer import Signer
import oci.data_science as data_science
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger("Model Deployment Example")

def validate_json(data):
    if data["model_name"] == "":
        print("Please check the model_name in the model_deployment_config.json")
        return False
    return True

def get_input_data(file_path):
    with open(file_path, "r") as fh:
        input_data = yaml.safe_load(fh)
    return input_data

def prediction_helper(inputs, model_deployment_id, config_name):
    oci_config = oci.config.from_file(config_name, "DEFAULT")
    signer = Signer(
        tenancy=oci_config['tenancy'],
        user=oci_config['user'],
        fingerprint=oci_config['fingerprint'],
        private_key_file_location=oci_config['key_file'],
        pass_phrase=oci_config['pass_phrase']
    )
    data_science_client = data_science.DataScienceClient(config=oci_config)
    model_deployment = data_science_client.get_model_deployment(model_deployment_id=model_deployment_id)
    model_deployment_url = model_deployment.data.model_deployment_url
    response = requests.post(f'{model_deployment_url}/predict', json=inputs, auth=signer)
    if response.status_code == 200:
        return response.json()
    else:
        return {'prediction': [], 'status': response.status_code, 'reason': response.reason}

def call_prediction(model_deployment_id, config_name, input_file):
    fp = open('model_deployment_config.json')
    data = json.load(fp)
    if not (validate_json(data)):
        logger.error(f'Call predictions failed')
        return
    model_name = data["model_name"]
    dir_name = os.path.dirname(os.path.abspath(__file__))
    if input_file == "":
        input_folder = os.path.join(dir_name, 'test_inputs')
        file_path = input_folder + '/' + model_name + '.yaml'
    else:
        file_path = input_file
    model_dir = os.path.join(dir_name, model_name)
    # check if the model folder is in the current directory
    if not (os.path.exists(model_dir)):
        print("Model does not exist in the current directory.")
        return
    # check if the test input folder is in the current directory
    if not (os.path.exists(file_path)):
        print("Test input does not exist in the current directory.")
        return
    input_data = get_input_data(file_path)
    predictions = []
    for inputs in input_data['TEST_INPUTS']:
        try:
            if 'MODEL_TYPE' in input_data and input_data['MODEL_TYPE'] == 'Image':
                img_bytes = open(os.path.join(model_dir, inputs), 'rb').read()
                img_inputs = base64.b64encode(img_bytes).decode('utf8')
                predictions.append(prediction_helper(img_inputs, model_deployment_id, config_name))
            else:
                predictions.append(prediction_helper(inputs, model_deployment_id, config_name))
        except Exception as e:
            logger.info(traceback.format_exc())
            raise e
    print(predictions)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Testing for inference")
    parser.add_argument("--model_deployment_id", help="Model deployment ID")
    parser.add_argument("--oci_config_file", nargs="?", help="Config file containing OCID's", default="~/.oci/config")
    parser.add_argument("--input_file", nargs="?", help="Test input file path for prediction", default="")
    args = parser.parse_args()
    call_prediction(args.model_deployment_id, args.oci_config_file, args.input_file)