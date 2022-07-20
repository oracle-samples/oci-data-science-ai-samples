import argparse
import json
import logging
import os
import shutil
import sys
import requests
import tempfile
import oci
from oci.data_science.models import CreateModelDetails

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger("Model Deployment Example")

def downloadModelFile(modelUrl, newModelFileName) :
    r = requests.get(modelUrl, stream=True)
    logger.info("Starting to download model.")
    with open(newModelFileName, 'wb') as f:
        f.write(r.content)
    logger.info("Finished downloading model.")
    f.close()

def validate_json(data):
    if data["compartment_id"] == "" or data["project_id"] == "" :
        print("Please update the compartment_id or project_id in the model_deployment_config.json")
        return False
    return True

def upload_model(model_file_name, config_name):
    current_direc = os.listdir()
    model_id = ""
    try:
        # read oci config
        oci_config = oci.config.from_file(config_name, "DEFAULT")
        ds_client = oci.data_science.DataScienceClient(config=oci_config)
        # create a zip file if the model exists in the directory
        if model_file_name in current_direc:
            with tempfile.TemporaryDirectory() as temp_dir:
                
                # automatically download model file to respective directory
                if model_file_name == "PyTorch_ResNet152":
                    downloadModelFile('https://download.pytorch.org/models/resnet152-b121ed2d.pth', model_file_name + '/' + model_file_name + '.ph')
                elif model_file_name == "TF_ResNet152":
                    downloadModelFile('https://tfhub.dev/google/imagenet/resnet_v1_152/classification/5?tf-hub-format=compressed', model_file_name + '/' + model_file_name + '.tar.gz')

                fp = open('model_deployment_config.json')
                data = json.load(fp)
                del data['model_id']
                model_zip = model_file_name + '.zip'
                if not (validate_json(data)):
                    fp.close()
                    logger.error(f'Model artifact upload failed.')
                    return
                logger.info(f"Starting to upload the model artifact: {data['deployment_name']}")
                dir_name = os.path.dirname(os.path.abspath(__file__))
                model_dir = os.path.join(dir_name, model_file_name)
                model_zip_name = os.path.splitext(model_zip)[0]
                zip_dir = os.path.join(temp_dir, model_zip_name)
                shutil.copytree(model_dir, zip_dir)
                shutil.make_archive(model_zip_name, 'zip', temp_dir, model_zip_name)
                # upload the model to catalog
                create_model_details = CreateModelDetails(
                    display_name= model_file_name,
                    project_id= data['project_id'],
                    compartment_id= data['compartment_id'],
                )
                model = ds_client.create_model(create_model_details).data
                assert model.id is not None, 'Create Model Details failed.'
                with open(model_zip, 'rb') as data:
                    ds_client.create_model_artifact(
                        model.id,
                        data,
                        content_disposition=f'attachment; filename="{model_zip_name}.zip"'
                    )
                fp.close()
                logger.info(f'Finished uploading model artifacts.')
                logger.info(f"Model ID: {model.id}")
                model_id = model.id
                # write the model id to the end of the json file
                with open('model_deployment_config.json', 'r+') as f:
                    data = json.load(f)
                    data['model_id'] = model.id
                    data['model_name'] = model_file_name
                    f.seek(0)
                    json.dump(data, f, indent = 4)
                    f.truncate()
                return model
            return True
        # Model does not exist
        else:
            logger.info(f'Model does not exist in the current directory.')
            return False
    except Exception as e:
        if model_id != "":
            ds_client.delete_model(model.id)
            logger.info(f'Deleting Model Artifact')
        raise e

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Testing for model artifact creation")
    parser.add_argument("--model_file_name", help="Name of the model to be created ")
    parser.add_argument("--oci_config_file", nargs="?", help="Config file containing OCID's", default="~/.oci/config")
    args = parser.parse_args()
    upload_model(args.model_file_name, args.oci_config_file)
