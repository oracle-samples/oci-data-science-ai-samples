import ads
ads.set_auth(auth="resource_principal", client_kwargs={"fs_service_endpoint": "https://pxch6velt3jybrrmzja7p74bam.apigateway.us-ashburn-1.oci.customer-oci.com/20230101"})

import os
os.environ.setdefault("CRYPTOGRAPHY_OPENSSL_NO_LEGACY", "1")

from ads.feature_store.feature_group import FeatureGroup
import pandas as pd
bike_feature_group = FeatureGroup.from_id("<featuregroup_id>")

# Datasets are provided as a convenience. Datasets are considered third-party content and are not considered materials under your agreement with Oracle.
# Citibike dataset is used in this notebook.You can access the citibike dataset license here - https://ride.citibikenyc.com/data-sharing-policy

# bike_df = pd.read_csv("https://raw.githubusercontent.com/oracle-samples/oci-data-science-ai-samples/main/notebook_examples/data/201901-citibike-tripdata.csv")

bike_df = pd.read_csv("oci://<dataset_uri>/201901-citibike-tripdata.csv")
bike_df.columns = bike_df.columns.str.replace(' ', '')

from pyspark.sql import SparkSession

spark = SparkSession \
        .builder \
        .appName("feature store example") \
        .enableHiveSupport() \
        .getOrCreate()

if bike_feature_group:
    bike_feature_group.materialise(bike_df)

df = bike_feature_group.select().read()
print(df.columns)