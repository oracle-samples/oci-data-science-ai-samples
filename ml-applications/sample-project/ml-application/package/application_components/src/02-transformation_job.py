import logging
import os
import warnings

import oci
import pandas as pd
from ocifs import OCIFileSystem
from sklearn.preprocessing import QuantileTransformer
from sklearn.utils import resample

warnings.filterwarnings('ignore')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Transformation")
LABEL_COLUMN_NAME = 'fetal_health'


def transform_data(storage_opts, input_file_uri, output_file_uri):
    logger.info("****** Starting data transformation .... ******")

    logger.info(f"Reading raw data from '{input_file_uri}'")
    df = pd.read_csv(filepath_or_buffer=input_file_uri,
                     storage_options=storage_opts,
                     index_col=False)
    logger.info(df)

    drop_columns(df)

    df = upsample_data(df, LABEL_COLUMN_NAME)
    df = scale_features(df, LABEL_COLUMN_NAME)

    remove_old_data(output_file_uri, storage_opts)

    logger.info(f"Uploading training data to '{output_file_uri}' ...")
    df.to_csv(output_file_uri,
              storage_options=storage_opts,
              sep=',',
              index=False)
    logger.info("Training data has been uploaded to object storage successfully")

    logger.info("****** Data transformation has been finished successfully .... ******")


def drop_columns(df):
    columns_to_drop = ['baseline value', 'histogram_number_of_peaks', 'histogram_median']
    logger.info(f"Dropping columns with names {columns_to_drop}")
    df.drop(columns_to_drop, axis=1, inplace=True)
    logger.info(df)


def upsample_data(df, label_col):
    logger.info("Starting upsampling process ....")

    # Mapping the labels to strings
    df[label_col] = df[label_col].map({1.0: '1 - Normal', 2.0: '2 - Risky', 3.0: '3 - Abnormal'})

    # Separate majority and minority classes
    df_majority = df[df[label_col] == '1 - Normal']
    df_minority_2 = df[df[label_col] == '2 - Risky']
    df_minority_3 = df[df[label_col] == '3 - Abnormal']

    # Upsample minority class
    df_minority_2_upsampled = resample(df_minority_2,
                                       replace=True,  # sample with replacement
                                       n_samples=len(df_majority),  # to match majority class
                                       random_state=123)  # reproducible results

    df_minority_3_upsampled = resample(df_minority_3,
                                       replace=True,  # sample with replacement
                                       n_samples=len(df_majority),  # to match majority class
                                       random_state=123)  # reproducible results
    logger.info(len(df_majority))
    logger.info(len(df_minority_2))
    logger.info(len(df_minority_3))

    # Combine majority class with upsampled minority class
    df_upsampled = pd.concat([df_majority, df_minority_2_upsampled, df_minority_3_upsampled])
    logger.info(df_upsampled)
    logger.info("Upsampling process has been finished successfully")
    return df_upsampled


def scale_features(recom, label_col):
    logger.info("Scaling the features ...")
    # Initialize the QuantileTransformer
    scaler = QuantileTransformer(output_distribution="normal")

    # Fit and transform the features, excluding the label column
    scaled_features = scaler.fit_transform(recom.drop(columns=[label_col]))

    # Create a new DataFrame with the scaled features
    scaled_df = pd.DataFrame(scaled_features, columns=recom.columns.difference([label_col]), index=recom.index)

    # Add the label column back to the DataFrame
    scaled_df[label_col] = recom[label_col]

    logger.info(scaled_df)
    logger.info("Scaling the features has been finished successfully")

    return scaled_df


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


def get_file_uri(filename_env_variable_name):
    output_file_name = get_env_variable(filename_env_variable_name)
    instance_bucket = get_env_variable("INSTANCE_BUCKET_NAME")
    instance_namespace = get_env_variable("OS_NAMESPACE")
    output_file_uri = f"oci://{instance_bucket}@{instance_namespace}/{output_file_name}"
    return output_file_uri


def main():
    input_file_uri = get_file_uri("INPUT_FILE")
    output_file_uri = get_file_uri("OUTPUT_FILE")

    auth_config = create_auth_config()

    transform_data(auth_config, input_file_uri, output_file_uri)


if __name__ == '__main__':
    main()
