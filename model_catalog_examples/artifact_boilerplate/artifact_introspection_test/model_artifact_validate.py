#!/usr/bin/env python3

import argparse
import ast
import json
import logging
import os
import shutil
import tempfile
import zipfile
from typing import Tuple
import re
from urllib.parse import urlparse
import oci
import os

import requests
import yaml

logger = logging.getLogger()
logging.basicConfig(level=logging.DEBUG)

_cwd = os.path.dirname(__file__)

TESTS_PATH = os.path.join(_cwd, 'resources', 'tests.yaml')
HTML_PATH = os.path.join(_cwd, 'resources', 'template.html')
CONFIG_PATH = os.path.join(_cwd, 'resources', 'config.yaml')
INDEX_PATH = os.path.dirname(__file__)+'/index.json'
PYTHON_VER_PATTERN = "^([3])(\.[6-9])(\.\d+)?$"
TESTS = {
    'score_py': {'key': 'score_py', 'category': 'Mandatory Files Check', 'description': 'Check that the file "score.py" exists and is in the top level directory of the artifact directory', 'error_msg': 'The file \'score.py\' is missing.'},
    'runtime_yaml': {'category': 'Mandatory Files Check', 'description': 'Check that the file "runtime.yaml" exists and is in the top level directory of the artifact directory', 'error_msg': 'The file \'runtime.yaml\' is missing.'},
    'score_syntax': {'category': 'score.py', 'description': 'Check for Python syntax errors', 'error_msg': 'There is Syntax error in score.py: '},
    'score_load_model': {'category': 'score.py', 'description': 'Check that load_model() is defined', 'error_msg': 'Function load_model is not present in score.py.'},
    'score_predict': {'category': 'score.py', 'description': 'Check that predict() is defined', 'error_msg': 'Function predict is not present in score.py.'},
    'score_predict_data': {'category': 'score.py', 'description': 'Check that the only required argument for predict() is named "data"', 'error_msg': 'The predict function in score.py must have a formal argument named \'data\'.'},
    'score_predict_arg': {'category': 'score.py', 'description': 'Check that all other arguments in predict() are optional and have default values', 'error_msg': 'All formal arguments in the predict function must have default values, except that \'data\' argument.'},
    'runtime_version': {'category': 'runtime.yaml', 'description': 'Check that field MODEL_ARTIFACT_VERSION is set to 3.0', 'error_msg': 'In runtime.yaml, the key MODEL_ARTIFACT_VERSION must be set to 3.0.'},
    'runtime_env_python': {'category': 'conda_env', 'description': 'Check that field MODEL_DEPLOYMENT.INFERENCE_PYTHON_VERSION is set to a value of 3.6 or higher', 'error_msg': 'In runtime.yaml, the key MODEL_DEPLOYMENT.INFERENCE_PYTHON_VERSION must be set to a value of 3.6 or higher.'},
    'runtime_env_path': {'category': 'conda_env', 'description': 'Check that field MODEL_DEPLOYMENT.INFERENCE_ENV_PATH is set', 'error_msg': 'In runtime.yaml, the key MODEL_DEPLOYMENT.INFERENCE_ENV_PATH must have a value.'},
    'runtime_path_exist': {'category': 'conda_env', 'description': 'check that the file path in MODEL_DEPLOYMENT.INFERENCE_ENV_PATH is correct.', 'error_msg': "In runtime.yaml, the key MODEL_DEPLOYMENT.INFERENCE_ENV_PATH does not exist."},
    }

def combine_msgs(test_list) -> str:
    '''
    For a given test_list combine all error_msg if test failed
    '''
    msgs = [TESTS[test]['error_msg'] for test in test_list if not TESTS[test].get('success')]
    return '\n'.join(msgs)

def model_deployment_find_fields(cfg) -> None:
    '''
    Recursively checks in MODEL_DEPLOYMENT if INFERENCE_ENV_SLUG, INFERENCE_ENV_TYPE, INFERENCE_ENV_PATH
    Also saves its value if present.
    '''
    if not isinstance(cfg, dict):
        return
    for key, value in cfg.items():
        if key == 'INFERENCE_ENV_PATH':
            TESTS['runtime_env_path']['success'] = True
            TESTS['runtime_env_path']['value'] = value
        elif key == 'INFERENCE_PYTHON_VERSION':
            m = re.match(PYTHON_VER_PATTERN, str(value))
            if m and m.group():
                TESTS['runtime_env_python']['success'] = True
                TESTS['runtime_env_python']['value'] = value
        else:
            model_deployment_find_fields(value)

def get_object_storage_client(client_kwargs=None):
    rp_version = os.environ.get(
                "OCI_RESOURCE_PRINCIPAL_VERSION", "UNDEFINED")
    config = None
    if rp_version == "UNDEFINED":
        config = oci.config.from_file()
    else:
        config = oci.auth.signers.get_resource_principals_signer()
    return oci.object_storage.ObjectStorageClient(config)

def check_runtime_yml(file_path) -> Tuple[bool, str]:
    '''
    Check runtime yaml mandatory fields
    '''

    with open(file_path, 'r') as ymlfile:
        cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)

    if not isinstance(cfg, dict):
        return False, 'runtime.yaml is not valid.'

    model_artifact_version = cfg.get('MODEL_ARTIFACT_VERSION')  # if not present None
    if model_artifact_version == '3.0':
        TESTS['runtime_version']['success'] = True
    else:
        logger.error(f'MODEL_ARTIFACT_VERSION: {model_artifact_version}')
        TESTS['runtime_version']['success'] = False
        return False, TESTS['runtime_version']['error_msg']

    model_deployment = cfg.get('MODEL_DEPLOYMENT')
    model_deployment_find_fields(model_deployment)
    test_list = ['runtime_env_python', 'runtime_env_path']
    for test in test_list:
        if 'success' not in TESTS[test]:
            TESTS[test]['success'] = False
    msg = combine_msgs(test_list)
    if msg:
        return False, msg
    try:
        m = re.match(PYTHON_VER_PATTERN, str(TESTS['runtime_env_python']['value']))
        if m and m.group():
            TESTS['runtime_env_python']['success']  = True
            try:
                with open(INDEX_PATH, "r") as index_file:
                    conda_pack_data = json.load(index_file)
            except Exception as e:
                return False, str(e)
            service_pack_list = conda_pack_data.get('service_packs')
            env_path = TESTS['runtime_env_path']['value']
            service_pack = next(filter(lambda d: env_path in d['pack_path'], service_pack_list), None)
            if service_pack:
                TESTS['runtime_path_exist']['success'] = True
                return True, True
            else:
                    url_parse = urlparse(env_path)
                    bucket_name = url_parse.username
                    namespace = url_parse.hostname
                    object_name = url_parse.path.strip("/")
                    if bucket_name != None and namespace != None and object_name != None:
                        try:
                            object_storage_client = get_object_storage_client()
                            head_object_response = object_storage_client.head_object(
                                namespace_name=namespace,
                                bucket_name=bucket_name,
                                object_name=object_name,
                                version_id=None,
                                if_match=None,
                                if_none_match=None,
                                opc_client_request_id=None,
                                opc_sse_customer_algorithm=None,
                                opc_sse_customer_key=None,
                                opc_sse_customer_key_sha256=None)
                            TESTS['runtime_path_exist']['success'] = True
                            return True, True
                        except:
                            TESTS['runtime_path_exist']['success'] = None
                            TESTS['runtime_path_exist']['error_msg'] = 'WARNING: Unable to validate if INFERENCE_ENV_PATH exists. Please check whether provided path is correct or user is authorized to access the file'
                            return False, TESTS['runtime_path_exist']['error_msg']
                    else:
                        TESTS['runtime_path_exist']['success'] = False
                        return False, TESTS['runtime_path_exist']['error_msg']
        else:
            logger.error(f'Mismatch in python version')
            TESTS['runtime_env_python']['success']  = False
            return False, TESTS['runtime_env_python']['error_msg']

    except Exception as e:
        return False, str(e)

def check_score_file(file_path) -> Tuple[bool, str]:
    '''
    Change current working directory to temporary directory and validate python file
    '''
    with open(file_path) as f:
        source = f.read()
    try:
        ast_module = ast.parse(source)

        TESTS['score_syntax']['success'] = True  # passed syntax check

        present_functions = {}
        for node in ast_module.body:
            if isinstance(node, ast.FunctionDef):
                present_functions[node.name] = {
                    'args': node.args.args,
                    'defaults': node.args.defaults
                }

        TESTS['score_predict']['success'] = 'predict' in present_functions
        TESTS['score_load_model']['success'] = 'load_model' in present_functions

        msg = combine_msgs(['score_predict', 'score_load_model'])
        if msg:
            return False, msg

        # check if predict function take required argument 'data' and all others are optional with default values
        predict_fn = present_functions['predict']
        if predict_fn['args'][0].arg == 'data':
            TESTS['score_predict_data']['success'] = True
            if len(predict_fn['defaults']) == len(predict_fn['args']) - 1:
                TESTS['score_predict_arg']['success'] = True
                return True, 'score.py is valid.'
            else:
                TESTS['score_predict_arg']['success'] = False
                return False, TESTS['score_predict_arg']['error_msg']
        else:
            TESTS['score_predict_data']['success'] = False
            return False, TESTS['score_predict_data']['error_msg']

    except SyntaxError as e:
        TESTS['score_syntax']['success'] = False
        TESTS['score_syntax']['error_msg'] = TESTS['score_syntax']['error_msg'] + str(e) # error message has ": " e has syntax error details
        return False, TESTS['score_syntax']['error_msg']

def check_mandatory_files(files_present) -> Tuple[bool, str]:
    '''
    Check if score.py and runtime.yaml are present or not.
    '''
    filename_list = [os.path.basename(fileName)for fileName in  files_present]
    TESTS['score_py']['success'] = 'score.py' in filename_list
    TESTS['runtime_yaml']['success'] = 'runtime.yaml' in filename_list

    msg = combine_msgs(['score_py', 'runtime_yaml'])
    if msg:
        return False, msg
    else:
        return True, 'All mandatory files are present.'

def validate_artifact(artifact) -> Tuple[bool, str]:
    '''
    Unzip the artifact zip file passed. Check for test cases.
    The method returns the status of check and error message if any.
    :artifact: str
    '''
    output_msg = 'Validation Passed.'
    success = True
    # create temporary folder and unzip model artifact
    temp_path=''
    try:
        if artifact.endswith('.zip'):
            temp_path = tempfile.mkdtemp(dir='.')
            with zipfile.ZipFile(artifact) as zip_ref:

                files_present = zip_ref.namelist()
                _status, _msg = check_mandatory_files(files_present)
                if not _status:
                    raise Exception(_msg)
                for file_name in files_present:
                    folder_list = file_name.split('/')
                    if len(folder_list) <= 2:
                        base_file_name = folder_list[-1]
                        if os.path.basename(base_file_name ) in ['score.py', 'runtime.yaml']:
                            source = zip_ref.open(file_name)
                            target = open(os.path.join(temp_path, os.path.basename(file_name)), "wb")
                            with source, target:
                                shutil.copyfileobj(source, target)
        elif os.path.isdir(artifact):
            files_present = os.listdir(artifact)
            _status, _msg = check_mandatory_files(files_present)
            print(files_present)
            if not _status:
                raise Exception(_msg)
        else:
            raise Exception("Invalid Artifact Path")
        if temp_path:
            dir_path = temp_path
        else:
            dir_path = artifact

        _status, _msg = check_score_file(os.path.join(dir_path, 'score.py'))
        if not _status:
            raise Exception(_msg)

        _status, _msg = check_runtime_yml(os.path.join(dir_path, 'runtime.yaml'))
        if not _status:
            raise Exception(_msg)
    except Exception as e:
        output_msg = str(e)
        success = False
    finally:
        if temp_path:
            shutil.rmtree(temp_path)
    return success, output_msg

RESULT_LIST =[True, False, None]
def get_test_result(test_id) -> int:
    '''
    Gives a number based on test result:
    0: test was success
    1: test failed
    2: didn't run test
    '''
    success = TESTS[test_id].get('success')
    return RESULT_LIST.index(success)

def write_html(output_path) -> None:
    '''
    writes an html file to output_path based on TESTS
    '''
    css_classes = ['pass', 'fail', 'no-test']
    out_classes = ['Passed', 'Failed', 'Not Tested']
    count_classes = ['odd', 'even']
    category = ''
    html_response = f'<body style="background-color:#F0FFFF; margin:10;padding:30"><h2>Introspection Tests Results</h2><br><br>'
    count = 0
    for key, value in TESTS.items():
        result = get_test_result(key)
        html_response += f'<tr class="{css_classes[result]}"><th class="{count_classes[count%2]}">{count}</th><td>{key}</td><td>{TESTS[key]["description"]}</td><td>{out_classes[result]}</td>'
        if get_test_result(key) == 1 or (key == 'runtime_path_exist' and "WARNING" in TESTS[key]['error_msg']):
            html_response += f'<td>{TESTS[key]["error_msg"]}</td></tr></body>'
        else:
            html_response += f'<td> </td></tr></body>'
        count += 1
    html_template = '<html><style>body{font-family:Arial,Helvetica,sans-serif}table{border-collapse:collapse font-family: arial, sans-serif}td,th{padding:0em 0em 0.7em 0.7em}.no-test{background-color:#E7E30C}.fail{background-color:#E73A0C}.pass{background-color:#1CCE70}.odd{background-color:#eef}.even{background-color:white}</style><body><table><tr><th></th><th>Test key</th><th>Test Name</th><th>Result</th><th>Message</th></tr> %s</table></body></html>'
    with open(output_path, 'w') as f:
        f.write(html_template %(html_response))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Model Artifact Validation')
    required_args = parser.add_argument_group('required arguments:')
    required_args.add_argument('--artifact', required=True, help='Enter path of model artifact zip file.')

    args = parser.parse_args()
    success, output_msg = validate_artifact(args.artifact)

    # Output Files
    HTML_OUTPUT = 'test_html_output.html'
    JSON_OUTPUT = 'test_json_output.json'

    logger.info('Output files are available in the same folder as {JSON_OUTPUT} and {HTML_OUTPUT}')

    write_html(HTML_OUTPUT)
    with open(JSON_OUTPUT, "w") as f:
        TESTS['Final_message'] = output_msg
        json.dump(TESTS, f, indent = 4)
    logger.info(output_msg)
