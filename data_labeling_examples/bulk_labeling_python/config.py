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
SERVICE_ENDPOINT_DP = f"https://datalabeling-dp.{REGION_IDENTIFIER}.oci.oraclecloud.com"
# ocid of the DLS Dataset
DATASET_ID = "ocid1.datalabelingdatasetint.oc1.uk-london-1.amaaaaaaniob46iaqml2zdzd6wuhw27awc6nj2tnug72m765lfhdz2pzwwzq"
# the no of processes to be used for parallel execution by default is set to maximum no of processors in the system
NO_OF_PROCESSORS = mp.cpu_count()
# Type of Annotation
# Possible values for ANNOTATION_TYPE "BOUNDING_BOX", "CLASSIFICATION"
ANNOTATION_TYPE = "CLASSIFICATION"
##############################################################################################################
# If ANNOTATION_TYPE is "CLASSIFICATION" edit classification_config.py
# If ANNOTATION_TYPE is "BOUNDING_BOX" edit bounding_box__config.py
