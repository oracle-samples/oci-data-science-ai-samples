from upload_model import *
from deploy_model import *
from call_prediction import *

def run_example(model_file_name, project_id, compartment_id, oci_config_file, input_file):
    if project_id != "" or compartment_id != "":
        with open('model_deployment_config.json', 'r+') as f:
            data = json.load(f)
            if project_id != "":
                data['project_id'] = project_id
            if compartment_id != "":
                data['compartment_id'] = compartment_id
            f.seek(0)
            json.dump(data, f, indent=4)
            f.truncate()
    # upload model
    upload_state = upload_model(model_file_name, oci_config_file)
    if not upload_state:
        return
    # deploy model
    md = ModelDeployment(oci_config_file)  # initialize a model deployment
    md.create_model_deployment()  # create a model deployment
    md.write_model_deployment_info()  # get a model deployment
    # call predictions
    fp = open('model_deployment_config.json')
    data = json.load(fp)
    call_prediction(data["model_deployment_id"], oci_config_file, input_file)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="End to end testing for model deployment")
    parser.add_argument("--model_file_name", help="Name of the model to be created ")
    parser.add_argument("--project_id", nargs="?", help="Project ID information", default="")
    parser.add_argument("--compartment_id", nargs="?", help="Compartment ID information", default="")
    parser.add_argument("--oci_config_file", nargs="?", help="Config file containing OCID's", default="~/.oci/config")
    parser.add_argument("--input_file", nargs="?", help="Test input file path for prediction", default="")
    args = parser.parse_args()
    run_example(args.model_file_name, args.project_id, args.compartment_id, args.oci_config_file, args.input_file)