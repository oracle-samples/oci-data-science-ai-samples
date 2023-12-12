from ads.feature_store.feature_group import FeatureGroup
import pandas as pd
import ads
ads.set_auth(auth="resource_principal", client_kwargs={"service_endpoint": "https://fnk6p6iswuttzxwffxq6uwpj2u.apigateway.us-ashburn-1.oci.customer-oci.com/20230101"})
ehr_feature_group = FeatureGroup.from_id("FED8117CDF1EE54F5A742EFFA2A88433")
patient_result_df = pd.read_csv("https://objectstorage.us-ashburn-1.oraclecloud.com/p/hh2NOgFJbVSg4amcLM3G3hkTuHyBD-8aE_iCsuZKEvIav1Wlld-3zfCawG4ycQGN/n/ociodscdev/b/oci-feature-store/o/beta/data/EHR/data-ori.csv")
if ehr_feature_group:
    ehr_feature_group.materialise(patient_result_df)