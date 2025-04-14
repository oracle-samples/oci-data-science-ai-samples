import logging
import os
import tempfile
import warnings

import ads
import oci
import pandas as pd
from ads.common.auth import AuthType
from ads.common.model_metadata import UseCaseType
from ads.dataset.factory import DatasetFactory
from ads.model.framework.xgboost_model import XGBoostModel
from ads.model.model_properties import ModelProperties
from oci.data_science.models import (
    ModelDeployment,
    ModelConfigurationDetails,
    UpdateModelConfigurationDetails,
    UpdateSingleModelDeploymentConfigurationDetails,
    UpdateModelDeploymentDetails
)
from sklearn.metrics import accuracy_score
from xgboost import XGBClassifier

warnings.filterwarnings('ignore')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Training")

LABEL_COLUMN_NAME = 'fetal_health'


def train_and_update_model(auth_config, model_compartment_id, model_deployment_id, instance_id, input_file_uri, tag_namespace):
    # trans = (get_input_data(auth_config))
    logger.info(f"Reading training data from '{input_file_uri}'")
    df = pd.read_csv(filepath_or_buffer=input_file_uri,
                     storage_options=auth_config,
                     index_col=False)
    logger.info(df)

    # MAPPING LABELS TO NUMERICAL VALUES
    # TODO why we map this to string label in transformation and back in training
    ds3 = mapping_labels(df, LABEL_COLUMN_NAME)

    # SPLITTING THE TRANSFORMED DATA
    selected_features, X_train, X_test, y_train, y_test = split_data(ds3)

    # TRAINING
    train_model(X_train, X_test, y_train, y_test)

    # XGBCLASSIFIER FITTING
    xgb_classifier = fit_xgb(ds3, selected_features, LABEL_COLUMN_NAME)

    # UPLOAD TO MODEL CATALOG
    model_id = upload_model_to_catalog(xgb_classifier, X_test, y_test, model_compartment_id,
                                       instance_id=instance_id, tag_namespace=tag_namespace)

    # DEPLOYMENT
    update_model_deploy(model_id, model_deployment_id, auth_config)


def get_input_data(storage_opts):
    input_file = get_env_variable("INPUT_FILE")
    instance_bucket = get_env_variable("INSTANCE_BUCKET_NAME")
    namespace = get_env_variable("OS_NAMESPACE")
    input_file_uri = f"oci://{instance_bucket}@{namespace}/{input_file}"

    logger.info(f"Reading raw data '{input_file_uri}'")
    return pd.read_csv(filepath_or_buffer=input_file_uri,
                       storage_options=storage_opts,
                       index_col=False)


def mapping_labels(trans, label_col):
    trans[label_col] = trans[label_col].map({'1 - Normal': 0, '2 - Risky': 1, '3 - Abnormal': 2})
    ds3 = DatasetFactory.from_dataframe(trans).set_target(label_col)
    logger.info(type(ds3))
    return ds3


def split_data(ds3):
    logger.info("Splitting the transformed data.....")
    train, test = ds3.train_test_split(0.25)
    X_train = train.X
    X_test = test.X
    y_train = train.y
    y_test = test.y
    selected_features = train.X.columns
    return selected_features, X_train, X_test, y_train, y_test


def train_model(X_train, X_test, y_train, y_test):
    logger.info("Training the data with XGBClassifier....")
    model_accuracy = pd.DataFrame(columns=['Model', 'Accuracy', 'Train_acc'])
    models = {
        'XGBClassifier': XGBClassifier(n_estimators=200, learning_rate=0.1, eval_metric='mlogloss')
    }
    for model_name, clf in models.items():
        clf.fit(X_train, y_train)
        y_pred = clf.predict(X_test)
        acc = accuracy_score(y_test, y_pred)
        train_pred = clf.predict(X_train)
        train_acc = accuracy_score(y_train, train_pred)
        logger.info(f"Accuracy: {acc}")
        # Use concat instead of append
        new_row = pd.DataFrame([[model_name, acc, train_acc]], columns=['Model', 'Accuracy', 'Train_acc'])
        model_accuracy = pd.concat([model_accuracy, new_row], ignore_index=True)

    # TODO ask what to do with this model accuracy (is it evaluation?)
    model_accuracy = model_accuracy.sort_values(ascending=False, by='Accuracy')
    logger.info(model_accuracy)


def fit_xgb(ds3, selected_features, label_col):
    logger.info("Starting model training with XGBoostClasifier...")
    df4 = ds3
    df4 = df4[list(selected_features) + [label_col]]
    train, test = df4.train_test_split(0.25)
    xgb_classifier = XGBClassifier(n_estimators=200, learning_rate=0.1, eval_metric='mlogloss')
    xgb_classifier.fit(train.X, train.y)
    logger.info("Model has been trained successful")
    return xgb_classifier


def upload_model_to_catalog(xgb_classifier, x_test, y_test, compartment_id, instance_id, tag_namespace):
    logger.info(f"Creating new trained Model in Model Catalog (compartment '{compartment_id}') ...")
    artifact_dir = tempfile.mkdtemp()

    conda_env = get_env_variable("CONDA_ENV_SLUG")
    project_id = get_env_variable("PROJECT_ID")
    xgb_model = XGBoostModel(estimator=xgb_classifier,
                             artifact_dir=artifact_dir,
                             properties=ModelProperties(
                                 compartment_id=compartment_id,
                                 project_id=project_id))
    xgb_model.prepare(
        inference_conda_env=conda_env,
        training_conda_env=conda_env,
        use_case_type=UseCaseType.MULTINOMIAL_CLASSIFICATION,
        X_sample=x_test,
        y_sample=y_test,
    )
    logger.info(os.listdir(artifact_dir))

    model_id = xgb_model.save(display_name='fetal_health_model',
                              # needed for tenant isolation
                              defined_tags={tag_namespace: {"MlApplicationInstanceId": instance_id}},
                              # needed for ML App to be able to track created model
                              freeform_tags={"MlApplicationInstance": instance_id})
    logger.info(f"Trained model has been created with ID = '{model_id}' ...")
    return model_id


def update_model_deploy(model_id, model_deployment_id, auth_config):
    logger.info(f"Updating Model Deployment '{model_deployment_id}' with Model {model_id}")
    ds_client = oci.data_science.DataScienceClient(signer=auth_config['signer'], config=auth_config.get('config'))

    model_deployment_data: ModelDeployment = ds_client.get_model_deployment(
        model_deployment_id
    ).data
    model_configuration_details: ModelConfigurationDetails = (model_deployment_data
                                                              .model_deployment_configuration_details
                                                              .model_configuration_details)

    update_model_config_details = UpdateModelConfigurationDetails(
        bandwidth_mbps=model_configuration_details.bandwidth_mbps,
        instance_configuration=model_configuration_details.instance_configuration,
        scaling_policy=model_configuration_details.scaling_policy,
        model_id=model_id
    )

    update_model_deployment_config_details = UpdateSingleModelDeploymentConfigurationDetails(
        deployment_type=model_deployment_data.model_deployment_configuration_details.deployment_type,
        model_configuration_details=update_model_config_details
    )

    update_model_deployment_details = UpdateModelDeploymentDetails(
        display_name=model_deployment_data.display_name,
        model_deployment_configuration_details=update_model_deployment_config_details
    )

    ds_client.update_model_deployment(
        model_deployment_id=model_deployment_id,
        update_model_deployment_details=update_model_deployment_details)

    logger.info(
        "Model Deployment update request has been sent successful (without waiting for asynchronous update finish)")


def get_env_variable(env_variable_name: str) -> str:
    value = os.getenv(env_variable_name)
    if value is None:
        raise ValueError(f"Environment variable '{env_variable_name}' for Ingestion Job not specified")
    return value


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
        ads.set_auth(auth=AuthType.SECURITY_TOKEN, profile=oci_profile)
    else:
        # API key authentication
        logger.info("API Key authentication")
        signer = oci.signer.Signer.from_config(oci_config)
        ads.set_auth(auth=AuthType.API_KEY, profile=oci_profile)

    auth_config = {"config": oci_config, "signer": signer}
    return auth_config


def create_resource_principal_auth_config() -> dict:
    logger.info("Using resource principal for authentication")
    resource_principal_signer = oci.auth.signers.get_resource_principals_signer()
    auth_config = {"signer": resource_principal_signer, "config": {}}
    ads.set_auth(**auth_config)
    return auth_config


def get_file_uri(filename_env_variable_name):
    output_file_name = get_env_variable(filename_env_variable_name)
    instance_bucket = get_env_variable("INSTANCE_BUCKET_NAME")
    instance_namespace = get_env_variable("OS_NAMESPACE")
    output_file_uri = f"oci://{instance_bucket}@{instance_namespace}/{output_file_name}"
    return output_file_uri


def main():
    instance_id = get_env_variable("INSTANCE_ID")
    model_compartment_id = get_env_variable("MODEL_COMPARTMENT_ID")
    model_deployment_id = get_env_variable("MODEL_DEPLOYMENT_ID")
    input_file_uri = get_file_uri("INPUT_FILE")
    tag_namespace = get_env_variable("MLAPPS_TAG_NAMESPACE")

    auth_config = create_auth_config()

    train_and_update_model(auth_config=auth_config,
                           model_compartment_id=model_compartment_id,
                           model_deployment_id=model_deployment_id,
                           instance_id=instance_id,
                           input_file_uri=input_file_uri,
                           tag_namespace=tag_namespace)


if __name__ == '__main__':
    main()
