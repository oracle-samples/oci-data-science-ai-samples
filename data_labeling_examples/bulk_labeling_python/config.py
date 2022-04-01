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
# compartment where DLS Dataset exists
COMPARTMENT_ID = "ocid1.compartment.oc1..aaaaaaaamrnszmfhl7xzawtef3rl6gmsb62tcoag32yiv5ujorognkuzrqfq"
# ocid of the DLS Dataset
DATASET_ID = "ocid1.datalabelingdatasetint.oc1.uk-london-1.amaaaaaaniob46iarr2zttq7c5th3jfqwab7d3vrq4daa52tcnnwhkgrowca"
# an array where the elements are all of the labels that you will use to annotate records in your DLS Dataset with.
# Each element is a separate label.
LABELS = ["dog", "cat"]
# the algorithm that will be used to assign labels to DLS Dataset records
LABELING_ALGORITHM = "FIRST_LETTER_MATCH"
# use for first_match labeling algorithm
FIRST_MATCH_REGEX_PATTERN = r'^([^/]*)/.*$'
# maximum number of DLS Dataset records that can be retrieved from the list_records API operation for labeling
# limit=1000 is the hard limit for list_records
LIST_RECORDS_LIMIT = 1000
# For CUSTOM_LABEL_MATCH specify the label map
LABEL_MAP = {"dog/": ["dog", "tommy"], "cat/": ["cats", "meow"]}
# the no of processes to be used for parallel execution by default is set to maximum no of processors int he system
NO_OF_PROCESSORS = mp.Pool(mp.cpu_count())
