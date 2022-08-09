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
    if token_path is None:
        # This is local run, so use our API Key.
        config = oci.config.from_file(file_location, profile_name)
        kwargs['config'] = config
        if 'signer' in kwargs:
            kwargs.pop('signer')
        authenticated_client = client(**kwargs)
    else:
        # This is Data Flow run, so use Delegation Token.
        with open(token_path) as fd:
            delegation_token = fd.read()
        signer = oci.auth.signers.InstancePrincipalsDelegationTokenSigner(
            delegation_token=delegation_token
        )
        kwargs['signer'] = signer
        kwargs['config'] = {}
        authenticated_client = client(**kwargs)
    return authenticated_client


class DataflowSession:
    def __init__(self, app_name=SAMPLE_APP_NAME, token_key=SAMPLE_TOKEN_KEY):
        self.app_name = app_name
        self.token_key = token_key
