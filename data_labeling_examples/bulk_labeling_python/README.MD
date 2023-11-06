# Annotate bulk number of records in OCI Data Labeling Service (DLS)
Introduction to Bulk Labeling Utility [demo video](https://otube.oracle.com/media/Bulk+Labeling+Utility/1_6jv76ouj)

## Data Labeling Service (DLS) Bulk-Labeling tool

Bulk-Labeling Tool provides the following scripts:

**1. Upload files to object storage bucket**

**upload_files_script**: This script takes the path to the dataset directory, along with the object storage bucket name and namespace of the bucket as input and uploads the files present in the given directory to the given object storage bucket.

**2. Bulk labeling records in Data Labeling Service**

**bulk_labeling_script**: This script can be used to annotate records of type classification (single-label, multi-label) as well as of type bounding-box.

For Single-Label and Multi-label type records
    This script labels all the records within the dataset by applying a labeling algorithm to get the matching label. Currently, following labeling algorithms are supported:

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
For Bounding-Box type annotation
    The script bulk labels records of type bounding box given the following details in the csv.
    Sample csv is attached in the bulk_labeling_python folder.

    - CSV Format Columns
    ```
    record_id: the ocid of the record to be annotated
    the co-ordinates of bounding box [(x1,y1), (x2,y2), (x3,y3), (x4,y4)
    x1: the normalized x1 co-ordinate of bounding box with range(0,1)
    x2: the normalized x2 co-ordinate of bounding box with range(0,1)
    x3: the normalized x3 co-ordinate of bounding box with range(0,1)
    x4: the normalized x4 co-ordinate of bounding box with range(0,1)
    y1: the normalized y1 co-ordinate of bounding box with range(0,1)
    y2: the normalized y2 co-ordinate of bounding box with range(0,1)
    y3: the normalized y3 co-ordinate of bounding box with range(0,1)
    y4: the normalized y4 co-ordinate of bounding box with range(0,1)
    label: the label of the record in the list format. e.g. the label can be ["dog"] or
           even multiple labels can be provided in the list ["dog", "pup"]
    ```
**3. Remove labels of records in Data Labeling Service**

**RemoveLabelScript:** This script takes REMOVE_LABEL_PREFIX as input and remove the labels from records which are matching with REMOVE_LABEL_PREFIX.
REMOVE_LABEL_PREFIX will be a label name, or label name prefix or '*'.

If '*' is given as REMOVE_LABEL_PREFIX then it will remove all labels from all records.

```
Consider a dataset having following records:
cat1.jpeg, cat2.jpeg, dog1.jpeg, dog2.jpeg
Labels in dataset: dog, pup, cat, kitten
    cat1.jpeg will be labeled with cat label
    cat2.jpeg will be labeled with cat and kitten labels
    dog1.png will be labeled with dog label
    dog2.png will be labeled with dog and pup labels
    
1. If REMOVE_LABEL_PREFIX = 'c' then it will remove label 'cat' from all labeled records. Dataset will be as folows :
    cat1.jpeg -> unlabeled
    cat2.jpeg will be labeled with kitten labels
    dog1.png will be labeled with dog label
    dog2.png will be labeled with dog and pup labels
    
2. If REMOVE_LABEL_PREFIX = 'd' then it will remove label 'dog' from all labeled records. Dataset will be as folows :
    cat1.jpeg will be labeled with cat label
    cat2.jpeg will be labeled with kitten labels
    dog1.png -> unlabeled
    dog2.png will be labeled with dog and pup labels

3. If REMOVE_LABEL_PREFIX = '*' then it will remove all labels from all labeled records. Dataset will be as folows :
    cat1.jpeg -> unlabeled
    cat2.jpeg -> unlabeled
    dog1.png -> unlabeled
    dog2.png -> unlabeled
```
### Requirements
1. An Oracle Cloud Infrastructure account. <br/>
2. A user created in that account, in a group with a policy that grants the desired permissions. This can be a user for yourself, or another person/system that needs to call the API. <br/>
3. A key pair used for signing API requests, with the public key uploaded to Oracle. Only the user calling the API should be in possession of the private key. For more information, see [Configuring the SDK](https://docs.oracle.com/en-us/iaas/tools/python/2.62.0/installation.html#install). <br/> 
4. Python 3.0.0+ <br/>
5. Follow this link to setup [SDK for Python](https://docs.oracle.com/en-us/iaas/Content/API/SDKDocs/pythonsdk.htm). This link will help you to install python, setup virtual environment, PyPi etc. 
6. Install Pandas using PIP. Run below command in terminal :
    ```
   pip install pandas
   ```

### Configurations

Add the following configurations in config.py, bounding_box_config.py, 
classification_config.py file in the project to run the scripts:

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
SERVICE_ENDPOINT_OBJECT_STORAGE = f"https://objectstorage.{REGION_IDENTIFIER}.oraclecloud.com"
# ocid of the DLS Dataset
DATASET_ID = "ocid1.datalabelingdatasetint.oc1.uk-london-1.amaaaaaaniob46ia7fsk45ghmfxcdkqnjrdzk2nprbhxijqzclm7qntvo4ya"
# the no of processes to be used for parallel execution by default is set to maximum no of processors in the system
NO_OF_PROCESSORS = mp.cpu_count()
# Type of Annotation
# Possible values for ANNOTATION_TYPE "BOUNDING_BOX", "CLASSIFICATION"
ANNOTATION_TYPE = "BOUNDING_BOX"

#Files present inside this directory will be uploaded to the object storage bucket
DATASET_DIRECTORY_PATH = "/Users/rahulprakash/Documents/Dataset"
#Object storage bucket name where the dataset will be uploaded
OBJECT_STORAGE_BUCKET_NAME = "Bulk-Labelling-bucket"
#Namespace of the object storage bucket
OBJECT_STORAGE_NAMESPACE = "idgszs0xipmn"

##############################################################################################################
# If ANNOTATION_TYPE is "CLASSIFICATION" edit classification_config.py
# If ANNOTATION_TYPE is "BOUNDING_BOX" edit bounding_box__config.py
```

```
# maximum number of DLS Dataset records that can be retrieved from the list_records API operation for labeling
# limit=1000 is the hard limit for list_records
LIST_RECORDS_LIMIT = 1000
# the algorithm that will be used to assign labels to DLS Dataset records
# Possible values for labeling algorithm "FIRST_LETTER_MATCH", "FIRST_REGEX_MATCH", "CUSTOM_LABELS_MATCH"
LABELING_ALGORITHM = "CUSTOM_LABELS_MATCH"
# an array where the elements are all of the labels that you will use to annotate records in your DLS Dataset with.
# Each element is a separate label.
LABELS = ["dog", "cat"]

# use for first_match labeling algorithm
FIRST_MATCH_REGEX_PATTERN = r'^([^/]*)/.*$'

# For CUSTOM_LABEL_MATCH specify the label map
LABEL_MAP = {"dog/": ["dog", "pup"], "cat/": ["cat", "kitten"]}
```

```
# the path of the csv file
PATH = "/Users/puneetmittal/Desktop/input_data.csv"
```

### Running the Utility
1. Open Terminal on your system. 
2. Clone the repository.
```
git clone https://github.com/oracle-samples/oci-data-science-ai-samples.git
```
3. Go to data_labeling_examples/bulk_labeling_python directory
```
cd data_labeling_examples/bulk_labeling_python
```
4. Run the below script to upload files to object storage bucket.
```
python3 upload_files_script.py
```
5. Run the below script to bulk label by "FIRST_LETTER_MATCH"/"FIRST_REGEX_MATCH"/"CUSTOM_LABELS_MATCH" labeling algorithm.
```
python3 bulk_labeling_script.py
```

6. Run the below script to remove labels from records
```
python3 remove_label_script.py
```

Note : Before running any of the above script please ensure to set the required configuration in config.py, classification_config.py and bounding_box_config.py.