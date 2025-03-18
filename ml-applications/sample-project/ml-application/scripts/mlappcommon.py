import fnmatch
import hashlib
import json
import os
import sys
import time
from typing import List, Dict

import oci
import yaml
from oci.data_science.models import WorkRequestLogEntry, CreateMlApplicationInstanceDetails, CreateIdcsAuthConfigurationDetails, CreateIdcsCustomServiceAuthConfigurationDetails, CreateIamAuthConfigurationCreateDetails

INSTANCE_VIEW_OCID_PREFIX = "cid1.datasciencemlappinstanceview"

INSTANCE_OCID_PREFIX = "cid1.datasciencemlappinstance"

GREEN = "\033[92m"
BLUE = '\033[94m'
ENDC = '\033[0m'  # Reset to default color


def print_green_message(msg: str):
    print(f"{GREEN}{msg}{ENDC}")

def print_blue_message(msg: str):
    print(f"{BLUE}{msg}{ENDC}")


def print_error(msg: str, exit_code=None):
    print(msg, file=sys.stderr)
    if exit_code is None:
        return
    else:
        sys.exit(exit_code)


def full_package_file_name(app_name, impl_version):
    return f"{app_name}-full-package-{impl_version}.zip"


def impl_package_file_name(impl_name, impl_version):
    return f"{impl_name}-package-{impl_version}.zip"


def create_signer(env_config: dict):
    # Set up the config with your OCI account details
    oci_config = oci.config.from_file(profile_name=env_config["oci_profile"])
    data_science_config = {"region": env_config["region"]}
    signer = None

    if 'security_token_file' in oci_config:
        # token authentication
        token_file = oci_config['security_token_file']
        token = None
        with open(token_file, 'r') as f:
            token = f.read()
        private_key = oci.signer.load_private_key_from_file(oci_config['key_file'])
        signer = oci.auth.signers.SecurityTokenSigner(token, private_key)
    else:
        # api key authentication
        signer = oci.signer.Signer.from_config(oci_config)

    return signer


def init_data_science_client(env_config: dict) -> oci.data_science.DataScienceClient:
    signer = None
    try:
        # resource principal authentication
        signer = oci.auth.signers.get_resource_principals_signer()
        print(f"Trying to initialize Data Science client with Resource Principals "
              f"and service_endpoint: {env_config.get('datascience_service_endpoint_url')}")
        data_science = oci.data_science.DataScienceClient(config={},
                                                          service_endpoint=env_config.get(
                                                              "datascience_service_endpoint_url"),
                                                          signer=signer)
    except EnvironmentError as e:
        print("Resource principal authentication unavailable due to: {}".format(e))
        # Set up the config with your OCI account details
        oci_config = oci.config.from_file(profile_name=env_config["oci_profile"])
        data_science_config = {"region": env_config["region"]}
        if 'security_token_file' in oci_config:
            # token authentication
            token_file = oci_config['security_token_file']
            token = None
            with open(token_file, 'r') as f:
                token = f.read()
            private_key = oci.signer.load_private_key_from_file(oci_config['key_file'])
            signer = oci.auth.signers.SecurityTokenSigner(token, private_key)
        else:
            # api key authentication
            signer = oci.signer.Signer.from_config(oci_config)
            for key in ['key_file', 'user', 'fingerprint', 'tenancy']:
                data_science_config[key] = oci_config[key]

        # Initialize the Data Science client
        print(f"Initializing Data Science client with following configuration: {data_science_config} "
              f"and service_endpoint: {env_config.get('datascience_service_endpoint_url')}")
        data_science = oci.data_science.DataScienceClient(data_science_config,
                                                          service_endpoint=env_config.get(
                                                              "datascience_service_endpoint_url"),
                                                          signer=signer)
    return data_science


def print_new_logs(client: oci.data_science.DataScienceClient, work_request_id, last_log_index):
    log_entries: List[WorkRequestLogEntry] = []
    page = None
    while True:
        if page is None:
            log_entries_response = client.list_work_request_logs(work_request_id)
        else:
            log_entries_response = client.list_work_request_logs(work_request_id, page=page)

        if not log_entries_response.data:
            break

        log_entries.extend(log_entries_response.data)
        if log_entries_response.next_page is None:
            break
        page = log_entries_response.next_page

    start_index = 0 if last_log_index is None else last_log_index + 1
    for i in range(start_index, len(log_entries)):
        log = log_entries[i]
        print(add_prefix_to_lines(log.message,
                                  BLUE + f"    WR LOG: {log.timestamp.strftime('%Y-%m-%d %H:%M:%S')}") + ENDC)

    if log_entries:
        last_log_index = len(log_entries) - 1
    return last_log_index


def add_prefix_to_lines(multiline_string, prefix):
    lines = multiline_string.split('\n')
    prefixed_lines = [prefix + line for line in lines]
    return '\n'.join(prefixed_lines)


def poll_work_request(client, work_request_id, timeout=6000):
    print("-----------------------------------------------------------")
    print(f"Polling status for WorkRequest {work_request_id}")
    delays = [5, 5, 10, 10, 10, 10, 10, 20, 30]  # Backoff delays
    last_log_index = None
    start_time = time.time()
    delay_index = 0

    while True:
        # Check if timeout has been reached
        if time.time() - start_time >= timeout:
            print(f"Timeout {timeout} sec reached. Polling stopped.")
            return

        # Poll WorkRequest status
        work_request: oci.data_science.models.WorkRequest = client.get_work_request(work_request_id).data
        print(f"Polling WorkRequest status = {work_request.status} (ID = {work_request_id})")
        # Get and print new logs
        last_log_index = print_new_logs(client, work_request_id, last_log_index)
        if work_request.status in ['IN_PROGRESS', 'ACCEPTED', 'CANCELING']:
            # Print next polling time
            delay = delays[delay_index] if delay_index < len(delays) else delays[-1]
            target_time = time.time() + delay
            print(f"Next polling in {delay} seconds "
                  f"(i.e. at '{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(target_time))}') ...")

            time.sleep(delay)

            # Increment delay index if not at the last value
            if delay_index < len(delays) - 1:
                delay_index += 1
        elif work_request.status in ['SUCCEEDED', 'FAILED', 'CANCELED']:
            print(f"WorkRequest reached final state '{work_request.status}'. Polling stopped")
            if (work_request.status != 'SUCCEEDED'):
                sys.exit(1)
            break
        else:
            print(f"WorkRequest in unexpected state: {work_request.status}. Polling stopped", work_request.status)
            break
    print("-----------------------------------------------------------")


def read_yaml(file_path):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)


def read_json(file_path: str):
    with open(file_path, 'r') as file:
        json_data = json.load(file)
        return json_data


def load_env_config(env_config_yaml_path: str, overrides: Dict[str, str] = {}):
    env_config: dict = read_yaml(env_config_yaml_path)
    env_config.update(overrides)
    return env_config


# TODO only first level is covered
def deserialize_oci_sdk_model_from_json(json_data, model_class):
    data = convert_keys_to_snake_case(json_data)

    if 'auth_configuration' in data and model_class is CreateMlApplicationInstanceDetails:
        data['auth_configuration'] = create_auth_configuration(data['auth_configuration'])

    # Return the deserialized model instance
    return model_class(**data)

def create_auth_configuration(data):
    type = data['type']
    if type == 'IDCS':
        return CreateIdcsAuthConfigurationDetails(**data)

    if type == 'IDCS_CUSTOM_SERVICE':
        return CreateIdcsCustomServiceAuthConfigurationDetails(**data)

    if type == 'IAM':
        return CreateIamAuthConfigurationCreateDetails(**data)
    else:
        raise Error(f"Unsupported auth type: {type}")


def camel_to_snake_case(camel_str):
    # This function converts a camelCase string to snake_case
    import re
    return re.sub(r'(?<!^)(?=[A-Z])', '_', camel_str).lower()


def convert_keys_to_snake_case(data):
    # Recursively convert all keys in a JSON-like data structure from camelCase to snake_case
    if isinstance(data, dict):
        new_data = {}
        for key, value in data.items():
            new_key = camel_to_snake_case(key)
            new_data[new_key] = convert_keys_to_snake_case(value)
        return new_data
    elif isinstance(data, list):
        return [convert_keys_to_snake_case(item) for item in data]
    else:
        return data


def copy_missing_items(source_dict: dict, target_dict: dict, key_mapping: dict):
    for key in key_mapping:
        if key not in source_dict:
            raise RuntimeError(f"Cannot find key {key} in source dictionary {source_dict}")
        elif key in source_dict and key_mapping and key_mapping[key] not in target_dict:
            target_dict[key_mapping[key]] = source_dict[key]


def append_naming_suffix(name: str, env_config: dict):
    return f"{name}{env_config['environment_naming_suffix']}"


def to_instance_view_ocid(instance_id: str) -> str:
    if INSTANCE_VIEW_OCID_PREFIX in instance_id:
        return instance_id
    else:
        return instance_id.replace(INSTANCE_OCID_PREFIX, INSTANCE_VIEW_OCID_PREFIX)


def to_instance_ocid(instance_view_id: str) -> str:
    return instance_view_id.replace(INSTANCE_VIEW_OCID_PREFIX, INSTANCE_OCID_PREFIX)


def prompt_to_confirm(msg):
    # Prompt the user for confirmation
    user_input = input(f"{msg} (Y/N): ")
    # Check if the user input is 'Y'
    return user_input == 'Y'


# Adds tag with hash for resource field to be able to detect if it was changed
def add_hash_tag(resource_fields: dict):
    if resource_fields.get('freeform_tags') is None:
        resource_fields['freeform_tags'] = {}
    if not isinstance(resource_fields.get('freeform_tags'), dict):
        raise ValueError("Field freeform_tags must be dictionary")
    resource_fields['freeform_tags']['hash'] = calculate_hash(resource_fields)


def calculate_hash(dictionary: dict):
    # Sort the dictionary and convert it to a JSON string to ensure consistency
    d_sorted = json.dumps(dictionary, sort_keys=True)
    # Create a hash object using SHA256 (you can choose other algorithms if you prefer)
    hash_object = hashlib.sha256(d_sorted.encode())
    # Return the hexadecimal representation of the hash
    return hash_object.hexdigest()
