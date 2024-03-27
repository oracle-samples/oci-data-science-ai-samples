import subprocess
import os
import shutil

from ads.feature_store.feature_group import FeatureGroup
import pandas as pd
import ads

home_dir = os.path.expanduser("~")
spark_conf_dir = os.path.join(home_dir, "spark_conf_dir")
common_jars_dir = os.path.join(spark_conf_dir, "common-jars")
datacatalog_metastore_client_jars_dir = os.path.join(spark_conf_dir, "datacatalog-metastore-client-jars")

conda_prefix = os.environ.get("CONDA_PREFIX")

os.environ["SPARK_CONF_DIR"] = spark_conf_dir
os.makedirs(spark_conf_dir, exist_ok=True)

shutil.copytree(f"{conda_prefix}/common-jars", common_jars_dir)
shutil.copytree(f"{conda_prefix}/datacatalog-metastore-client-jars", datacatalog_metastore_client_jars_dir)

shutil.copy(f"{conda_prefix}/spark-defaults.conf", os.path.join(spark_conf_dir, "spark-defaults.conf"))
shutil.copy(f"{conda_prefix}/core-site.xml", os.path.join(spark_conf_dir, "core-site.xml"))
shutil.copy(f"{conda_prefix}/log4j.properties", os.path.join(spark_conf_dir, "log4j.properties"))

COMPARTMENT_ID = "COMPARTMENT_ID"
METASTORE_ID = "METASTORE_ID"
SERVICE_ENDPOINT = "SERVICE_ENDPOINT"
FEATURE_GROUP_ID = "FEATURE_GROUP_ID"

print("Initiating feature store lazy entities creation")

compartment_id = os.environ.get(COMPARTMENT_ID, "ocid1.compartment...none")
metastore_id = os.environ.get(METASTORE_ID, "ocid1.metastore...none")
service_endpoint = os.environ.get(SERVICE_ENDPOINT, "<api_gateway_url>")
feature_group_id = os.environ.get(FEATURE_GROUP_ID, "<unique_id>")

print(subprocess.run(["odsc",
                "data-catalog",
                "config",
                "--authentication",
                "resource_principal",
                "--metastore",
                metastore_id],capture_output=True))

ads.set_auth(auth="resource_principal", client_kwargs={"fs_service_endpoint": service_endpoint})

ehr_feature_group = FeatureGroup.from_id(feature_group_id)
patient_result_df = pd.read_csv("https://objectstorage.us-ashburn-1.oraclecloud.com/p/hh2NOgFJbVSg4amcLM3G3hkTuHyBD-8aE_iCsuZKEvIav1Wlld-3zfCawG4ycQGN/n/ociodscdev/b/oci-feature-store/o/beta/data/EHR/data-ori.csv")
if ehr_feature_group:
    ehr_feature_group.materialise(patient_result_df)