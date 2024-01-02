import ads
ads.set_auth(auth="resource_principal", client_kwargs={"fs_service_endpoint": "<api_gateway>"})

import os
os.environ.setdefault("CRYPTOGRAPHY_OPENSSL_NO_LEGACY", "1")

from ads.feature_store.feature_group import FeatureGroup
import pandas as pd
ehr_feature_group = FeatureGroup.from_id("<featuregroup_id>>")
patient_result_df = pd.read_csv("oci://<dataset_uri>>/EHR_data-ori.csv")

from pyspark.sql import SparkSession

spark = SparkSession \
        .builder \
        .appName("feature store example") \
        .enableHiveSupport() \
        .getOrCreate()

if ehr_feature_group:
    ehr_feature_group.materialise(patient_result_df)

df = ehr_feature_group.select().read()
print(df.columns)