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
SERVICE_ENDPOINT_DP = f"https://dlstest-dp.{REGION_IDENTIFIER}.oci.oraclecloud.com"
# ocid of the DLS Dataset
DATASET_ID = "ocid1.datalabelingdatasetint.oc1.uk-london-1.amaaaaaaniob46ias33axzqmubpp5znqm7yl5kqvhunmrn7jxdl2pnjpd75q"
# an array where the elements are all of the labels that you will use to annotate records in your DLS Dataset with.
# Each element is a separate label.
LABELS = ["dog", "cat"]
# the algorithm that will be used to assign labels to DLS Dataset records
# Possible values for labeling algorithm "FIRST_LETTER_MATCH", "FIRST_REGEX_MATCH", "CUSTOM_LABELS_MATCH"
LABELING_ALGORITHM = "CUSTOM_LABELS_MATCH"
# use for first_match labeling algorithm
FIRST_MATCH_REGEX_PATTERN = r'^([^/]*)/.*$'
# maximum number of DLS Dataset records that can be retrieved from the list_records API operation for labeling
# limit=1000 is the hard limit for list_records
LIST_RECORDS_LIMIT = 1000
# For CUSTOM_LABEL_MATCH specify the label map
LABEL_MAP = {"dog/": ["dogs", "tommy"], "cat/": ["cats", "meow"]}
# the no of processes to be used for parallel execution by default is set to maximum no of processors in the system
NO_OF_PROCESSORS = mp.cpu_count()
