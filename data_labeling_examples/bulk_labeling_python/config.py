import multiprocessing as mp

# for help, run:
# python3 help.py

# config file path
CONFIG_FILE_PATH = "~/.oci/config"
# config file profile
CONFIG_PROFILE = "DEFAULT"
# region identifier of DLS Dataset
REGION_IDENTIFIER = "uk-london-1"
# service_endpoint
SERVICE_ENDPOINT_DP = f"https://dlsprod-dp.{REGION_IDENTIFIER}.oci.oraclecloud.com"
SERVICE_ENDPOINT_OBJECT_STORAGE = f"https://objectstorage.{REGION_IDENTIFIER}.oraclecloud.com"
# ocid of the DLS Dataset
DATASET_ID = "ocid1.datalabelingdatasetint.oc1.uk-london-1.amaaaaaaniob46iagvz2cg7rpwrpuqmqfcbuyyzqviqoseow5eaurg66pwhq"
# the no of processes to be used for parallel execution by default is set to maximum no of processors in the system
NO_OF_PROCESSORS = mp.cpu_count()
# Type of Annotation
# Possible values for ANNOTATION_TYPE "BOUNDING_BOX", "CLASSIFICATION"
ANNOTATION_TYPE = "CLASSIFICATION"
##############################################################################################################
# If ANNOTATION_TYPE is "CLASSIFICATION" edit classification_config.py
# If ANNOTATION_TYPE is "BOUNDING_BOX" edit bounding_box__config.py
#Prefix will be a label name, or label name prefix
REMOVE_LABEL_PRIFIX = "j"
#Files present inside this directory will be uploaded to the object storage bucket
DATASET_DIRECTORY_PATH = "/Users/rahulprakash/Documents/Dataset"
#Object storage bucket name where the dataset will be uploaded
OBJECT_STORAGE_BUCKET_NAME = "Tif-Testing"
#Namespace of the object storage bucket
OBJECT_STORAGE_NAMESPACE = "idgszs0xipmn"
