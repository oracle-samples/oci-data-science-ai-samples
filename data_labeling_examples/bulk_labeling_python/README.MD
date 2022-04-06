# Annotate bulk number of records in OCI Data Labeling Service (DLS)

## Data Labeling Service (DLS) Bulk-Labeling tool

Bulk-Labeling Tool provides following two scripts to facilitate bulk labeling records in Data Labeling Service:

1. **bulk_labeling_script**: This script labels all the records within the dataset by applying a labeling algorithm to get the matching label. Currently, following labeling algorithms are supported:

    
    - FIRST_LETTER_MATCH: The first letter of the DLS Dataset record's name must be equal to the first letter of the label that the record will be annotated with. The matching is not case-sensitive.
    
    ```
    Consider a dataset having following records: cat1.jpeg, cat2.jpeg, dog1.png, dog2.png
    Label Set: cat , dog 
    Result of FIRST_LETTER_MATCH labeling algorithm: 
    cat1.jpeg will be labeled with cat label
    cat2.jpeg will be labeled with cat label
    dog1.png will be labeled with dog label
    dog2.png will be labeled with dog label
    ```
    
    
    - FIRST_REGEX_MATCH: The regular expression (regex) pattern assigned to _FIRST_MATCH_REGEX_PATTERN_ will be applied to the DLS Dataset record's name, and the first capture group extracted must be equal to the label that the record will be annotated with.
    
    ```
    Consider a dataset having following records: PetCat1.jpeg, PetCat2.jpeg, PetDog1.png, PetDog2.png
    Label Set: cat , dog 
    FIRST_MATCH_REGEX_PATTERN : ^([^\/]*)\/.*$
    Result of FIRST_REGEX_MATCH labeling algorithm: 
    PetCat1.jpeg will be labeled with cat label
    PetCat2.jpeg will be labeled with cat label
    PetDog1.png will be labeled with dog label
    PetDog2.png will be labeled with dog label
    ```


    - CUSTOM_LABELS_MATCH: This algorithm takes object storage path as input along with the label that needs to be applied to records under that path. Only root level path is supported. Multiple labels can also be assigned to a given path. The labeling algorithm for this case is .

    ```
    Consider a dataset having following records:
    cat/cat1.jpeg, cat/cat2.jpeg, dog/dog1.jpeg, dog/dog2.jpeg
    Labels in dataset: dog, pup, cat, kitten
    CUSTOM_LABELS={ "dog/": ["dog","pup"], "cat/": ["cat", "kitten"] }
    Result of CUSTOM_LABELS_MATCH algorithm: 
        cat/cat1.jpeg will be labeled with cat and kitten labels
        cat/cat2.jpeg will be labeled with cat and kitten labels
        dog/dog1.png will be labeled with dog and pup labels
        dog/dog2.png will be labeled with dog and pup labels
    ```

### Requirements
1. An Oracle Cloud Infrastructure account. <br/>
2. A user created in that account, in a group with a policy that grants the desired permissions. This can be a user for yourself, or another person/system that needs to call the API. <br/>
3. A key pair used for signing API requests, with the public key uploaded to Oracle. Only the user calling the API should be in possession of the private key. For more information, see [Configuring the SDK](https://docs.oracle.com/en-us/iaas/tools/python/2.62.0/installation.html#install). <br/> 
4. Python 3.0.0+ <br/>

For more information [SDK for Python](https://docs.oracle.com/en-us/iaas/Content/API/SDKDocs/pythonsdk.htm)

### Configurations

Add the following configurations in config.properties file in the project to run the scripts:

```
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

# an array where the elements are all of the labels that you will use to annotate records in your DLS Dataset with. Each element is a separate label.
LABELS = ["dog", "cat"]

# the algorithm that will be used to assign labels to DLS Dataset records
LABELING_ALGORITHM = "FIRST_LETTER_MATCH"

# use for first_match labeling algorithm
FIRST_MATCH_REGEX_PATTERN = r'^([^/]*)/.*$'

# maximum number of DLS Dataset records that can be retrieved from the list_records API operation for labeling
# limit=1000 is the hard limit for list_records
LIST_RECORDS_LIMIT = 1000

# For CUSTOM_LABEL_MATCH specify the label map
LABEL_MAP = {"dog/": ["dog", "pup"], "cat/": ["cat", "kitten"]}

# the no of processes to be used for parallel execution by default is set to maximum no of processors in the system
NO_OF_PROCESSORS = mp.Pool(mp.cpu_count())
