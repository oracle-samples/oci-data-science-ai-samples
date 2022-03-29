# Annotate bulk number of records in OCI Data Labeling Service (DLS)

## Data Labeling Service (DLS) Bulk-Labeling tool

Bulk-Labeling Tool provides following two scripts to facilitate bulk labeling records in Data Labeling Service:

1. **SingleLabelDatasetBulkLabelingScript**: This script labels all the records within the dataset by applying a labeling algorithm to get the matching label. Currently following two labeling algorithm is supported:

    
    - FIRST_LETTER_MATCH: The first letter of the DLS Dataset record's name must be equal to the first letter of the label that the record will be annotated with. The matching is not case-sensitive.
     
    Consider a dataset having following records: cat1.jpeg, cat2.jpeg, dog1.png, dog2.png
    Label Set: cat , dog 
    Result of FIRST_LETTER_MATCH labeling algorithm: 
    cat1.jpeg will be labeled with cat label
    cat2.jpeg will be labeled with cat label
    dog1.png will be labeled with dog label
    dog2.png will be labeled with dog label
    
    
    - FIRST_REGEX_MATCH: The regular expression (regex) pattern assigned to _FIRST_MATCH_REGEX_PATTERN_ will be applied to the DLS Dataset record's name, and the first capture group extracted must be equal to the label that the record will be annotated with.
    
    Consider a dataset having following records: PetCat1.jpeg, PetCat2.jpeg, PetDog1.png, PetDog2.png
    Label Set: cat , dog 
    FIRST_MATCH_REGEX_PATTERN : ^([^\/]*)\/.*$
    Result of FIRST_REGEX_MATCH labeling algorithm: 
    PetCat1.jpeg will be labeled with cat label
    PetCat2.jpeg will be labeled with cat label
    PetDog1.png will be labeled with dog label
    PetDog2.png will be labeled with dog label
    
2. **CustomBulkLabelingScript**: This script takes object storage path as input along with the label that needs to be applied to records under that path. Only root level path is supported. Multiple labels can also be assigned to a given path. The labeling algorithm for this case is CUSTOM_LABELS_MATCH.

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
1. An Oracle Cloud Infrastructure account.
2. A user created in that account, in a group with a policy that grants the desired permissions. This can be a user for yourself, or another person/system that needs to call the API. 3. A key pair used for signing API requests, with the public key uploaded to Oracle. Only the user calling the API should be in possession of the private key. For more information, see [Configuring the SDK](https://docs.oracle.com/en-us/iaas/Content/API/SDKDocs/javasdkgettingstarted.htm#Configur).
4. Java 8 or Java 11.
5. A TTL value of 60. For more information, see [Configuring the SDK](https://docs.oracle.com/en-us/iaas/Content/API/SDKDocs/javasdkgettingstarted.htm#Configur).

For more information [SDK for Java](https://docs.oracle.com/en-us/iaas/Content/API/SDKDocs/javasdk.htm)

### Configurations

Add the following configurations in config.properties file in the project to run the scripts:

```
#Path of Config File
CONFIG_FILE_PATH=~/.oci/config

#Config Profile
CONFIG_PROFILE=DEFAULT

#DLS DP URL
DLS_DP_URL=https://dlstest-dp.${REGION}.oci.oraclecloud.com

#Region where dataset is created
REGION=uk-london-1

#Dataset Id whose record you want to bulk label
DATASET_ID=ocid1.compartment.oc1..aaaaaaaawob4faujxaqxqzrb555b44wxxrfkcpapjxwp4s4hwjthu46idr5a

#Number of Parallel Threads for Bulk Labeling. Default is 20
THREAD_COUNT=30

# Algorithm that will be used to assign labels to DLS Dataset records : FIRST_LETTER_MATCH, FIRST_REGEX_MATCH, CUSTOM_LABELS_MATCH
LABELING_ALGORITHM=FIRST_REGEX_MATCH

# Comma separated Input Label Set for FIRST_LETTER_MATCH, FIRST_REGEX_MATCH algorithm. Each element is a separate label.
LABELS=cat,dog

# Used for FIRST_REGEX_MATCH labeling algorithm to define the regex pattern
FIRST_MATCH_REGEX_PATTERN=^abc*

# JSON Request for CUSTOM_LABELS_MATCH labeling algorithm. The request consists of a Map of path and its corresponding list of labels that you want to apply to that path
CUSTOM_LABELS={ "dog/": ["dog","pup"], "cat/": ["cat", "kitten"] }