# Annotate bulk number of records in OCI Data Labeling Service (DLS)

Introduction to Bulk Labeling Utility [demo video](https://otube.oracle.com/media/Bulk+Labeling+Utility/1_6jv76ouj)
## Data Labeling Service (DLS) Bulk-Labeling tool

Bulk-Labeling Tool provides the following scripts :

**1. Upload files to object storage bucket**


**UploadToObjectStorageScript**: This script takes the path to the dataset directory, along with the object storage bucket name and namespace of the bucket as input and uploads the files present in the given directory to the given object storage bucket.

```
Consider having the directory with the following files:
cat1.jpg, dog1.jpeg, cat2.tiff, voucher.pdf

Result of UploadToObjectStorageScript algorithm:
 All the four files will be uploaded to the given object storage bucket.
```

**2. Bulk labeling records in Data Labeling Service**

1. **SingleLabelDatasetBulkLabelingScript**: This script labels all the records within the dataset by applying a labeling algorithm to get the matching label. Currently following two labeling algorithm is supported:


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

3. **BulkAssistedLabelingScript**: This script takes datasetId as input along with the labeling algorithm as ML_ASSISTED_LABELING. There are 3 different ways to use this script - 
    1. Use the pretrained model offered by the ai service to auto label records
    2. Provide the OCID of the custom ML model that you have trained separately using OCI ai services to auto label records
    3. Provide the training dataset so that the script can invoke model training internally and then auto label records

```
Consider a dataset with the following dataset labels - 
{Dog, Cat, Animal}
Let us consider picture of a cat - 
If the machine learning model suggests 4 labels -> {Cat, Carnivore, Animal, Mammal} for this image, only the labels that 
are provided in the DLS dataset details will be considered. 
i.e, Expected output is the image gets labeled as a {Cat, Animal} once the script executes.

Conditions - 

3. Ensure that the following assisted labeling specific params are set in config.properties file - 

    LABELING_ALGORITHM=ML_ASSISTED_LABELING (Required)
    ML_MODEL_TYPE (Required)
    CONFIDENCE_THRESHOLD (Required, default is 0.7)
    CUSTOM_MODEL_ID (Required only for using custom model, default is null)
    MODEL_TRAINING_PROJECT_ID (Required only for training a new model)
    TRAINING_DATASET_ID (Required only for training a new model)
    
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
3. A key pair used for signing API requests, with the public key uploaded to Oracle. Only the user calling the API should be in possession of the private key. For more information, see [Configuring the SDK](https://docs.oracle.com/en-us/iaas/Content/API/SDKDocs/javasdkgettingstarted.htm#Configur). <br/>
4. Java 8 or Java 11. <br/>
5. A TTL value of 60. For more information, see [Configuring the SDK](https://docs.oracle.com/en-us/iaas/Content/API/SDKDocs/javasdkgettingstarted.htm#Configur). <br/>

For more information [SDK for Java](https://docs.oracle.com/en-us/iaas/Content/API/SDKDocs/javasdk.htm)

### Additional requirements for Assisted Labeling Utility 
1. The group where the user is present needs to have the following policies: 
    a) AI Vision service access: 
    Quick set up of Vision policies using a template - https://docs.oracle.com/en-us/iaas/vision/vision/using/policies_quick_set_up.htm
    Manual set up of Vision policies - https://docs.oracle.com/en-us/iaas/vision/vision/using/about_vision_policies.htm
    
    b) AI Language service access:
    Manual set up of Language service policies - https://docs.oracle.com/en-us/iaas/language/using/policies.htm
    
### Training custom models with OCI AI services 

1. If you have a niche labeling use case which will not be covered by the pretrained models supplied by Vision/Language,
this route applies to you. 


### Running the Utility
1. Open Terminal on your system.
2. Verify that Java 8 or higher is installed in the system. In case you do not have java installed on your system, download it from https://www.oracle.com/java/technologies/downloads/

```
java -version
```
3. Clone the repository.

```
git clone https://github.com/oracle-samples/oci-data-science-ai-samples.git
```
4. Go to data_labeling_examples/bulk_labeling_java directory

```
cd data_labeling_examples/bulk_labeling_java
```
5. Run the below command to upload files to object storage bucket.

```
java -DCONFIG_FILE_PATH='~/.oci/config' -DCONFIG_PROFILE=DEFAULT -DOBJECT_STORAGE_URL=https://objectstorage.<REGION>.oraclecloud.com -DOBJECT_STORAGE_BUCKET_NAME=<BUCKET_NAME> -DOBJECT_STORAGE_NAMESPACE=<NAMESPACE> -DDATASET_DIRECTORY_PATH=<DIRECTORY_PATH> -cp libs/bulklabelutility-v3.jar com.oracle.datalabelingservicesamples.scripts.UploadToObjectStorageScript
```
6. Run the below command to bulk label by "FIRST_LETTER_MATCH" labeling algorithm.

```
java -DCONFIG_FILE_PATH='~/.oci/config' -DCONFIG_PROFILE=DEFAULT -DDLS_DP_URL=https://dlsprod-dp.<REGION>.oci.oraclecloud.com -DTHREAD_COUNT=20 -DDATASET_ID=ocid1.datalabelingdatasetint.oc1.phx.amaaaaaaniob46ia7ybplfjdfmohqxxmwpg4p6nftl4ypnuirvsljkzhlq3q -DLABELING_ALGORITHM=FIRST_LETTER_MATCH -DLABELS=cat,dog -cp libs/bulklabelutility-v3.jar com.oracle.datalabelingservicesamples.scripts.SingleLabelDatasetBulkLabelingScript
```
7. Run the below command to bulk label by "FIRST_REGEX_MATCH" labeling algorithm.

```
java -DCONFIG_FILE_PATH='~/.oci/config' -DCONFIG_PROFILE=DEFAULT -DDLS_DP_URL=https://dlsprod-dp.<REGION>.oci.oraclecloud.com -DTHREAD_COUNT=20 -DDATASET_ID=ocid1.datalabelingdatasetint.oc1.phx.amaaaaaaniob46ia7ybplfjdfmohqxxmwpg4p6nftl4ypnuirvsljkzhlq3q -DLABELING_ALGORITHM=FIRST_REGEX_MATCH -DFIRST_MATCH_REGEX_PATTERN=^abc* -DLABELS=cat,dog -cp libs/bulklabelutility-v3.jar com.oracle.datalabelingservicesamples.scripts.SingleLabelDatasetBulkLabelingScript
```
8. Run the below command to bulk label by "CUSTOM_LABELS_MATCH" labeling algorithm.

```
java -DCONFIG_FILE_PATH='~/.oci/config' -DCONFIG_PROFILE=DEFAULT -DDLS_DP_URL=https://dlsprod-dp.<REGION>.oci.oraclecloud.com -DTHREAD_COUNT=20 -DDATASET_ID=ocid1.datalabelingdatasetint.oc1.phx.amaaaaaaniob46ia7ybplfjdfmohqxxmwpg4p6nftl4ypnuirvsljkzhlq3q -DLABELING_ALGORITHM=CUSTOM_LABELS_MATCH -DCUSTOM_LABELS='{"dog/": ["dog"], "cat/": ["cat"] }' -cp libs/bulklabelutility-v3.jar com.oracle.datalabelingservicesamples.scripts.CustomBulkLabelingScript
```
9. Run the below command to bulk label by "ML_ASSISTED_LABELING" labeling algorithm.

Before you run the command, please understand the limitations of this utility.
1. If you choose a pretrained model to predict labels on the records, the DLS dataset labels should be a part of the supported categories for the auto labeling to provide results.

Supported labels for vision use cases are identifying scene-based features and common objects in an image.

Supported list of labels for language use cases can be found below - 
Pretrained model type  Supported labels 
Text Classifcation     https://docs.oracle.com/en-us/iaas/language/using/pretrain-models.htm#text-class
Named Entity Recognition https://docs.oracle.com/en-us/iaas/language/using/pretrain-models.htm#ner

2. If you choose to provide a custom model OCID, the predictions will depend on the trained model's quality. 

3. If you choose to train a new custom model using the utility, it always uses "quick training" - This option produces a model that is not fully optimized but is available in about an hour. 
If you are interested in using "recommended training" which can take upto 24 hours, please finish the training independently using the ai service console/SDK 
and use (ML_MODEL_TYPE=CUSTOM) to plug in the custom model OCID for auto labeling.

Known issues - 

Language service text classification returns the dominant category to which a particular text belongs. So, auto labeling is not supported for multilabel text classification usecase.

```
java -DCONFIG_FILE_PATH='~/.oci/config' -DCONFIG_PROFILE=DEFAULT -DTHREAD_COUNT=20 -DREGION=us-phoenix-1 -DLABELING_ALGORITHM=ML_ASSISTED_LABELING -DML_MODEL_TYPE=PRETRAINED -DCONFIDENCE_THRESHOLD=0.8 -DDATASET_ID=ocid1.datalabelingdataset.oc1.phx.amaaaaaaniob46ia4qae7hitbpxx6cmc6kmoowvxkckxmdlmdvtdprgibnsa -cp libs/bulklabelutility-v3.jar com.oracle.datalabelingservicesamples.scripts.BulkAssistedLabelingScript
```

10. Run the below command to remove labels from records
```
java -DCONFIG_FILE_PATH='~/.oci/config' -DCONFIG_PROFILE=DEFAULT -DDLS_DP_URL=https://dlstest-dp.<REGION>.oci.oraclecloud.com -DTHREAD_COUNT=20 -DDATASET_ID=ocid1.datalabelingdatasetint.oc1.phx.amaaaaaaniob46ia7ybplfjdfmohqxxmwpg4p6nftl4ypnuirvsljkzhlq3q -DREMOVE_LABEL_PREFIX='cat' -cp libs/bulklabelutility-v3.jar com.oracle.datalabelingservicesamples.scripts.RemoveLabelScript
```

Note: You can override any config using -D followed by the configuration name. The list of all configurations are mentioned in following section.

### Configurations

Following is the list of all configurations (src/main/resources/config.properties file) supported by the bulk labeling script:

```
#Path of Config File
CONFIG_FILE_PATH=~/.oci/config

#Config Profile
CONFIG_PROFILE=DEFAULT

#region identifier 
REGION=us-phoenix-1

#DLS DP URL
DLS_DP_URL=https://dlsprod-dp.<REGION>.oci.oraclecloud.com

#DLS CP URL
DLS_CP_URL=https://dlsprod-cp.<REGION>.oci.oraclecloud.com

#OBJECT STORAGE URL
OBJECT_STORAGE_URL=https://objectstorage.<REGION>.oraclecloud.com

#Dataset Id whose record you want to bulk label
DATASET_ID=ocid1.datalabelingdatasetint.oc1.phx.amaaaaaaniob46ia7ybplfjdfmohqxxmwpg4p6nftl4ypnuirvsljkzhlq3q

#Number of Parallel Threads for Bulk Labeling. Default is 20
THREAD_COUNT=20

# Algorithm that will be used to assign labels to DLS Dataset records : FIRST_LETTER_MATCH, FIRST_REGEX_MATCH, CUSTOM_LABELS_MATCH, ML_ASSISTED_LABELING
LABELING_ALGORITHM=FIRST_REGEX_MATCH

# Comma separated Input Label Set for FIRST_LETTER_MATCH, FIRST_REGEX_MATCH algorithm. Each element is a separate label.
LABELS=cat,dog

# Used for FIRST_REGEX_MATCH labeling algorithm to define the regex pattern
FIRST_MATCH_REGEX_PATTERN=^abc*

# JSON Request for CUSTOM_LABELS_MATCH labeling algorithm. The request consists of a Map of path and its corresponding list of labels that you want to apply to that path
CUSTOM_LABELS={ "dog/": ["dog","pup"], "cat/": ["cat", "kitten"] }

#Files present inside this directory will be uploaded to the object storage bucket
DATASET_DIRECTORY_PATH=/Users/rahulprakash/Documents/Dataset

#Object storage bucket name where the dataset will be uploaded
OBJECT_STORAGE_BUCKET_NAME=bucket-20220629-0913

#Namespace of the object storage bucket
OBJECT_STORAGE_NAMESPACE=idgszs0xipmn

#Prefix will be a label name, or label name prefix
REMOVE_LABEL_PREFIX=

## All the following inputs are only for ML_ASSISTED_LABELING algorithm :

# ML model type for assisted labeling, choices are PRETRAINED, CUSTOM and NEW
ML_MODEL_TYPE=PRETRAINED

# Optional parameters for ML_MODEL_TYPE=CUSTOM :
# ML model OCID for any vision/language trained model
CUSTOM_MODEL_ID=

# Optional parameters for ML_MODEL_TYPE=NEW :

# ML project OCID from vision/language service to create the model. If not provided, a new project is created
MODEL_TRAINING_PROJECT_ID=

# DLS dataset OCID with labeled records to be used as initial training data for creating custom model
TRAINING_DATASET_ID=

