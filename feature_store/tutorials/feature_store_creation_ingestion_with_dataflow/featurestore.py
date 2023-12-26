import ads
import os
import pandas as pd

ads.set_auth(auth="resource_principal", client_kwargs={"fs_service_endpoint": "<api_gateway"})

from ads.feature_store.feature_store import FeatureStore
from ads.feature_store.feature_group import FeatureGroup

import pandas as pd
os.environ.setdefault("CRYPTOGRAPHY_OPENSSL_NO_LEGACY", "1")

import ads
compartment_id = "<compartment_id>"
metastore_id = "<metastore_id>"

patient_result_df = pd.read_csv("oci://<dataset_uri>/EHR_data-ori.csv")

print(f"The dataset contains {patient_result_df.shape[0]} rows and {patient_result_df.shape[1]} columns")

# get all the features
features = [feat for feat in patient_result_df.columns if feat != 'SOURCE']
num_features = [feat for feat in features if patient_result_df[feat].dtype != object]
cat_features = [feat for feat in features if patient_result_df[feat].dtype == object]

print(f"Total number of features : {len(features)}")
print(f"Number of numerical features : {len(num_features)}")
print(f"Number of categorical features : {len(cat_features)}\n")
print(patient_result_df.isna().mean().to_frame(name='Missing %'))
print(patient_result_df.nunique().to_frame(name='# of unique values'))
feature_store_resource = (
    FeatureStore().
    with_description("Electronic Heath Data consisting of Patient Test Results").
    with_compartment_id(compartment_id).
    with_name("EHR details DataFlow").
    with_offline_config(metastore_id=metastore_id)
)
feature_store = feature_store_resource.create()
print(feature_store)
entity = feature_store.create_entity(
    name="EHR",
    description="Electronic Health Record predictions"
)
print(entity)

def chained_transformation(patient_result_df, **transformation_args):
    def label_encoder_transformation(patient_result_df, **transformation_args):
        from sklearn.preprocessing import LabelEncoder
        # creating instance of labelencoder
        labelencoder = LabelEncoder()
        result_df = patient_result_df.copy()
        column_labels = transformation_args.get("label_encode_column")
        if isinstance(column_labels, list):
            for col in column_labels:
                result_df[col] = labelencoder.fit_transform(result_df[col])
        elif isinstance(column_labels, str):
            result_df[column_labels] = labelencoder.fit_transform(result_df[column_labels])
        else:
            return None
        return result_df

    def min_max_scaler(patient_result_df, **transformation_args):
        from sklearn.preprocessing import MinMaxScaler
        final_result_df = patient_result_df.copy()
        scaler = MinMaxScaler(feature_range=(0, 1))
        column_labels = transformation_args.get("scaling_column_labels")
        final_result_df[column_labels] = scaler.fit_transform(final_result_df[column_labels])
        return patient_result_df

    def feature_removal(input_df, **transformation_args):
        output_df = input_df.copy()
        output_df.drop(transformation_args.get("redundant_feature_label"), axis=1, inplace=True)
        return output_df

    out1 = label_encoder_transformation(patient_result_df, **transformation_args)
    out2 = min_max_scaler(out1, **transformation_args)
    return feature_removal(out2, **transformation_args)


transformation_args = {
    "label_encode_column": ["SEX", "SOURCE"],
    "scaling_column_labels": num_features,
    "redundant_feature_label": ["MCH", "MCHC", "MCV"]
}

from ads.feature_store.transformation import Transformation, TransformationMode

transformation = (
    Transformation()
    .with_name("chained_transformation")
    .with_feature_store_id(feature_store.id)
    .with_source_code_function(chained_transformation)
    .with_transformation_mode(TransformationMode.PANDAS)
    .with_description("transformation to perform feature engineering")
    .with_compartment_id(compartment_id)
)

transformation.create()
from pyspark.sql import SparkSession

spark = SparkSession \
        .builder \
        .appName("feature store example") \
        .enableHiveSupport() \
        .getOrCreate()

feature_group_ehr = (
    FeatureGroup()
    .with_feature_store_id(feature_store.id)
    .with_primary_keys([])
    .with_name("ehr_feature_group")
    .with_entity_id(entity.id)
    .with_compartment_id(compartment_id)
    .with_schema_details_from_dataframe(patient_result_df)
    .with_transformation_id(transformation.id)
    .with_transformation_kwargs(transformation_args)
)
feature_group_ehr.create()

from ads.feature_store.feature_group_expectation import ExpectationType
from great_expectations.core import ExpectationSuite, ExpectationConfiguration

expectation_suite_ehr = ExpectationSuite(
    expectation_suite_name="test_hcm_df"
)
expectation_suite_ehr.add_expectation(
    ExpectationConfiguration(
        expectation_type="expect_column_values_to_not_be_null",
        kwargs={"column": "AGE"},
    )
)
expectation_suite_ehr.add_expectation(
    ExpectationConfiguration(
        expectation_type="expect_column_values_to_be_between",
        kwargs={"column": "HAEMOGLOBINS", "min_value": 0, "max_value": 30},
    )
)
from ads.feature_store.common.enums import ExpectationType

feature_group_ehr.with_expectation_suite(expectation_suite_ehr, expectation_type=ExpectationType.STRICT)
feature_group_ehr.update()

print(feature_group_ehr)
print("feature_group_ehr id " + feature_group_ehr.id)


