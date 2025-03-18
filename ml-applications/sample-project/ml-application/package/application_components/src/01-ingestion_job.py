import oci
import os
import pandas as pd
import warnings
import logging

from ocifs import OCIFileSystem

warnings.filterwarnings('ignore')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Ingestion")


def ingest_data(storage_opts: dict, input_file_uri: str, output_file_uri: str):
    logger.info("****** Running data ingestion ... ******")

    logger.info(f"Reading data from: {input_file_uri} ...")
    column_names = ['baseline value', 'accelerations', 'fetal_movement',
                    'uterine_contractions', 'light_decelerations', 'severe_decelerations',
                    'prolongued_decelerations', 'abnormal_short_term_variability',
                    'mean_value_of_short_term_variability',
                    'percentage_of_time_with_abnormal_long_term_variability',
                    'mean_value_of_long_term_variability', 'histogram_width',
                    'histogram_min', 'histogram_max', 'histogram_number_of_peaks',
                    'histogram_number_of_zeroes', 'histogram_mode', 'histogram_mean',
                    'histogram_median', 'histogram_variance', 'histogram_tendency',
                    'fetal_health']
    df = pd.read_csv(filepath_or_buffer=input_file_uri,
                     names=column_names,
                     sep=',',
                     header=0,
                     storage_options=storage_opts,
                     index_col=False)
    logger.info(df)

    logger.info("Starting data cleaning process...")
    df = df.dropna()
    logger.info("Data cleaning process has finished successfully")

    remove_old_data(output_file_uri, storage_opts)

    logger.info(f"Uploading ingested data to '{output_file_uri}' ...")
    logger.info(df)
    df.to_csv(path_or_buf=output_file_uri,
              storage_options=storage_opts,
              sep=',',
              index=False)
    logger.info(f"Ingested data uploaded to object storage")

    logger.info(f"****** Data ingestion process has been finished successfully ******")


def remove_old_data(output_file_uri, storage_opts):
    try:
        logger.info(f"Trying to clean up old data '{output_file_uri}' ...")
        fs = OCIFileSystem(signer=storage_opts['signer'], config=storage_opts.get('config'))
        fs.rm(output_file_uri, recursive=True)
        logger.info(f"Object '{output_file_uri}' removed")
    except FileNotFoundError:
        logger.info(f"Old object {output_file_uri} not found")


def create_auth_config() -> dict:
    oci_profile = os.getenv("OCI_PROFILE")
    if oci_profile is not None:
        return create_local_oci_profile_auth_config(oci_profile)
    else:
        return create_resource_principal_auth_config()


def create_local_oci_profile_auth_config(oci_profile) -> dict:
    logger.info(f"Using local OCI config with profile '{oci_profile}' for authentication")
    oci_config = oci.config.from_file(profile_name=oci_profile)
    signer = None
    if 'security_token_file' in oci_config:
        # Session token authentication
        logger.info("Session token authentication")
        token_file = oci_config['security_token_file']
        token = None
        with open(token_file, 'r') as f:
            token = f.read()
        private_key = oci.signer.load_private_key_from_file(oci_config['key_file'])
        signer = oci.auth.signers.SecurityTokenSigner(token, private_key)
    else:
        # API key authentication
        logger.info("API Key authentication")
        signer = oci.signer.Signer.from_config(oci_config)

    auth_config = {"config": oci_config, "signer": signer}
    return auth_config


def create_resource_principal_auth_config() -> dict:
    logger.info("Using resource principal for auth")
    resource_principal_signer = oci.auth.signers.get_resource_principals_signer()
    auth_config = {"signer": resource_principal_signer}
    return auth_config


def get_env_variable(env_variable_name):
    value = os.getenv(env_variable_name)
    if value is None:
        raise ValueError(f"Environment variable '{env_variable_name}' for Ingestion Job not specified")
    return value


def get_output_file_uri():
    output_file_name = get_env_variable("OUTPUT_FILE")
    instance_bucket = get_env_variable("INSTANCE_BUCKET_NAME")
    instance_namespace = get_env_variable("OS_NAMESPACE")
    output_file_uri = f"oci://{instance_bucket}@{instance_namespace}/{output_file_name}"
    return output_file_uri


def main():
    input_file_uri = get_env_variable("EXTERNAL_DATA_SOURCE")
    output_file_uri = get_output_file_uri()

    auth_config = create_auth_config()
    ingest_data(auth_config, input_file_uri, output_file_uri)


if __name__ == '__main__':
    main()
