import os

import oci
from pyspark.sql import SparkSession

DEFAULT_LOCATION = os.path.join('~', '.oci', 'config')
DEFAULT_PROFILE = "DEFAULT"

SAMPLE_APP_NAME = "ExampleApp"
SAMPLE_TOKEN_KEY = "spark.hadoop.fs.oci.client.auth.delegationTokenPath"


def get_spark_context(app_name=SAMPLE_APP_NAME, dataflow_session=None):
    if dataflow_session is not None:
        app_name = dataflow_session.app_name
    return SparkSession.builder.appName(app_name).getOrCreate()


def _get_token_path_(app_name=SAMPLE_APP_NAME, token_key=SAMPLE_TOKEN_KEY,
                     dataflow_session=None):
    if dataflow_session is not None:
        app_name = dataflow_session.app_name
        token_key = dataflow_session.token_key

    spark_context = get_spark_context(app_name)
    print(f"Obtained spark context for app-name [{app_name}]!")
    return spark_context.sparkContext.getConf().get(token_key)


def get_authenticated_client(client, app_name=SAMPLE_APP_NAME,
                             token_key=SAMPLE_TOKEN_KEY,
                             file_location=DEFAULT_LOCATION,
                             profile_name=DEFAULT_PROFILE,
                             dataflow_session=None, **kwargs):
    if dataflow_session is not None:
        app_name = dataflow_session.app_name
        token_key = dataflow_session.token_key

    token_path = _get_token_path_(app_name, token_key)
    print("Token with key [***] is available at path [***].")
    if token_path is None:
        config = oci.config.from_file(file_location, profile_name)
        print(f"Loaded oci config of {profile_name} from {file_location}.")
        kwargs['config'] = config
        if 'signer' in kwargs:
            kwargs.pop('signer')
    else:
        with open(token_path) as fd:
            delegation_token = fd.read()
            print("Read delegation token from path [***]!")
        signer = oci.auth.signers.InstancePrincipalsDelegationTokenSigner(
            delegation_token=delegation_token
        )
        print("Created signer using instance principal and delegation token.")
        kwargs['signer'] = signer
        kwargs['config'] = {}
    return client(**kwargs)


class DataflowSession:
    def __init__(self, app_name=SAMPLE_APP_NAME, token_key=SAMPLE_TOKEN_KEY):
        self.app_name = app_name
        self.token_key = token_key
