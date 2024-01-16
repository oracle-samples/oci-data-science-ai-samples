import ads
import os
import pandas as pd

ads.set_auth(auth="resource_principal", client_kwargs={"fs_service_endpoint": "<api_gateway"})

from ads.feature_store.feature_store import FeatureStore
from ads.feature_store.feature_group import FeatureGroup

os.environ.setdefault("CRYPTOGRAPHY_OPENSSL_NO_LEGACY", "1")

compartment_id = "<compartment_id>"
metastore_id = "<metastore_id>"

# Datasets are provided as a convenience. Datasets are considered third-party content and are not considered materials under your agreement with Oracle.
# Citibike dataset is used in this notebook.You can access the citibike dataset license here - https://ride.citibikenyc.com/data-sharing-policy

# bike_df = pd.read_csv("https://raw.githubusercontent.com/oracle-samples/oci-data-science-ai-samples/main/notebook_examples/data/201901-citibike-tripdata.csv")


bike_df = pd.read_csv("oci://<dataset_uri>/201901-citibike-tripdata.csv")
bike_df.columns = bike_df.columns.str.replace(' ', '')

print(f"The dataset contains {bike_df.shape[0]} rows and {bike_df.shape[1]} columns")


feature_store_resource = (
    FeatureStore().
    with_description("Data consisting of bike riders details").
    with_compartment_id(compartment_id).
    with_name("Bike details DataFlow").
    with_offline_config(metastore_id=metastore_id)
)
feature_store = feature_store_resource.create()
print(feature_store)
entity = feature_store.create_entity(
    name="Bike rides",
    description="bike riders"
)
print(entity)

from ads.feature_store.transformation import Transformation, TransformationMode

def is_round_trip(bike_df):
    bike_df['roundtrip'] = bike_df['startstationid'] == bike_df['endstationid']
    return bike_df

transformation = feature_store.create_transformation(
    transformation_mode=TransformationMode.PANDAS,
    source_code_func=is_round_trip,
    name="is_round_trip",
)

transformation.create()
from pyspark.sql import SparkSession

spark = SparkSession \
        .builder \
        .appName("feature store example") \
        .enableHiveSupport() \
        .getOrCreate()

feature_group_bike = (
    FeatureGroup()
    .with_feature_store_id(feature_store.id)
    .with_primary_keys([])
    .with_name("feature_group_bike")
    .with_entity_id(entity.id)
    .with_compartment_id(compartment_id)
    .with_schema_details_from_dataframe(bike_df)
    .with_transformation_id(transformation.id)
)
feature_group_bike.create()

from ads.feature_store.feature_group_expectation import ExpectationType
from great_expectations.core import ExpectationSuite, ExpectationConfiguration

expectation_suite = ExpectationSuite(expectation_suite_name="test_stop_time")
expectation_suite.add_expectation(
    ExpectationConfiguration(
        expectation_type="expect_column_values_to_not_be_null",
        kwargs={"column": "stoptime"}
    )
)
from ads.feature_store.common.enums import ExpectationType

feature_group_bike.with_expectation_suite(expectation_suite, expectation_type=ExpectationType.LENIENT)
feature_group_bike.update()

print(feature_group_bike)
print("feature_group_bike id " + feature_group_bike.id)