# Lab 4: Access OCI Vision with the Vision Python SDK

## Introduction

Oracle Cloud Infrastructure provides a number of Software Development Kits (SDKs) to facilitate development of custom solutions. SDKs allow you to build and deploy apps that integrate with Oracle Cloud Infrastructure services. Each SDK also includes tools and artifacts you need to develop an app, such as code samples and documentation. In addition, if you want to contribute to the development of the SDKs, they are all open source and available on GitHub.

You can invoke OCI Vision capabilities through the OCI SDKs.  In this lab session, we will show how to use the Python SDK to call the Vision service.

[SDK for Python](https://docs.oracle.com/en-us/iaas/Content/API/SDKDocs/pythonsdk.htm#SDK_for_Python)

*Estimated Lab Time*: 10 minutes

### Objectives:

* Learn how to use Vision Python SDK to communicate with our Vision service endpoints.

<!-- ### Prerequisites:
* Familiar with Python programming is required
* Familiar with local editing tools, vi and nano -->


## **TASK 1:** Setup API Signing Key and Config File

Mac OS / Linux:

```
mkdir ~/.oci
```
Windows:
```
mkdir %HOMEDRIVE%%HOMEPATH%\.oci
```

Generate an API signing key pair

1. Open User Settings

  Open the Profile menu (User menu icon) and click User Settings.
    ![](./images/userProfileIcon.png " ")

2. Open API Key

  Navigate to API Key and then Click Add API Key.
    ![](./images/addAPIButton.png " ")

3. Generate API Key

  In the dialog, select Generate API Key Pair. Click Download Private Key and save the key to your .oci directory and then click Add.
    ![](./images/genAPI.png " ")

4. Generate Config File

  Copy the values shown on the console.
    ![](./images/conf.png " ")

 Create a config file in the .oci folder and paste the values copied.
 Replace the key_file value with the path of your generated API Key.
    ![](./images/config2.png " ")



To Know more visit [Generating API KEY](https://docs.oracle.com/en-us/iaas/Content/API/Concepts/apisigningkey.htm) and [SDK and CLI Configuration File](https://docs.oracle.com/en-us/iaas/Content/API/Concepts/sdkconfig.htm#SDK_and_CLI_Configuration_File)

## **TASK 2:** Setup for Python

Please follow the steps in the order described.
Before you go any further, make sure you have Python 3.x version and that it’s available from your command line. You can check this by simply running:
```
python --version
```
If you do not have Python, please install the latest 3.x version from [python.org ](https://www.python.org)

Additionally, you’ll need to make sure you have pip available. You can check this by running:
```
pip --version
```
If you installed Python from source, with an installer from python.org, or via Homebrew you should already have pip. If you’re on Linux and installed using your OS package manager, you may have to install pip separately.


1. Create virtualenv

  To create a virtual environment, run the venv module as a script as shown below
```
python -m venv <name of virtual environment>
```
2. Activate virtualenv

  Once you’ve created a virtual environment, you may activate it.

Mac OS / Linux:
```
source <name of virtual environment>/bin/activate
```
Windows:
```
<name of virtual environment>\Scripts\activate
```
3. Install OCI

  Now Install oci by running:
```
pip install oci
```

## **TASK 3:** Add Sample Images to Object Storage

1. Download the [sample images](./Sample-Images).

2. Login to the OCI Console and navigate to your Object Storage Buckets

  ![](./images/ObjectStorageLink.png " ")
  
3. Create a new bucket called "pidaydemo".

4. Create a new folder in the "pidaydemo" bucket called "sample-images".

5. Upload the sample images to the "sample-images" folder.

## **TASK 4:** OCI Vision Service SDK Code Sample

#### Python Code
```Python
### Import Packages
import time
import oci
import json
import re

from oci.ai_vision import AIServiceVisionClient
from oci.ai_vision.models.create_image_job_details import CreateImageJobDetails
from oci.ai_vision.models.image_object_detection_feature import ImageObjectDetectionFeature
from oci.ai_vision.models.input_location import InputLocation
from oci.ai_vision.models.object_list_inline_input_location import ObjectListInlineInputLocation
from oci.ai_vision.models.object_location import ObjectLocation
from oci.ai_vision.models.object_storage_document_details import ObjectStorageDocumentDetails
from oci.ai_vision.models.output_location import OutputLocation
from oci.object_storage import ObjectStorageClient

### Define Variables
namespace_name = "<namespace name>"
bucket_name = "<bucket name>"
compartment_id = "<compartment id>"
input_prefix = "<folder name for images>"
output_prefix = "<output folder name for results>"

# Auth Config Definition
config = oci.config.from_file('~/.oci/config')

# AI Vision Client Definition
ai_vision_client = oci.ai_vision.AIServiceVisionClient(config)

### Get Images from Object Storage Using Object Storage Client
# List Objects in Bucket
object_storage_client = ObjectStorageClient(config)
object_list = object_storage_client.list_objects(
    namespace_name = namespace_name,
    bucket_name = bucket_name,
    prefix = input_prefix
)

# Create List of All Testing Images
image_list = []
for i in object_list.data.objects:
    if i.name.endswith('.jpg'):
        object_location = ObjectLocation()
        object_location.bucket_name = bucket_name
        object_location.namespace_name = namespace_name
        object_location.object_name= i.name
        image_list.append(object_location)

### Vision AI
# Send the Request to Service with Multiple Features
image_object_detection_feature = ImageObjectDetectionFeature()
features = [image_object_detection_feature]

# Setup Input Location
object_locations1 = image_list
input_location = ObjectListInlineInputLocation()
input_location.object_locations = object_locations1

# Setup Output Location
output_location = OutputLocation()
output_location.namespace_name = namespace_name
output_location.bucket_name = bucket_name
output_location.prefix = output_prefix

# Details Setup
create_image_job_details = CreateImageJobDetails()
create_image_job_details.features = features
create_image_job_details.compartment_id = compartment_id
create_image_job_details.output_location = output_location
create_image_job_details.input_location = input_location

# Send the testing images to Vision service by calling creat_image_job API to get analyze images and it returns json responses
res = ai_vision_client.create_image_job(create_image_job_details=create_image_job_details)

# Final Prefix Variable
final_prefix= output_prefix+"/"+res.data.id+"/"+namespace_name+"_"+bucket_name+"_"+input_prefix+"/"

# Logic to perform the following statistics:
# 1. Count the number of persons and hardhats in each image, and total up the counts
# 2. Report the person and hardhat counts, and the number of images processed
# 3. Also, list the names of images where the person count and hardhat count don’t match

# Sleep for 90 Seconds
print("Please wait 45 seconds for images to be analyzed.")
time.sleep(45)

person_count=0
hat_count=0
image_counter=0
no_match_list=[]

# List all JSON responses received by Vision AI
object_storage_client = ObjectStorageClient(config)
object_list = object_storage_client.list_objects(
    namespace_name = namespace_name,
    bucket_name = bucket_name,
    prefix = final_prefix
) 

# Count number of persons and number of hats 
for i in object_list.data.objects:
    image_counter=image_counter+1
    body=object_storage_client.get_object(namespace_name, bucket_name, object_name=i.name)
    dict_test= json.loads(body.data.content.decode('utf-8'))
    for j in dict_test['imageObjects']:
        if (j['name'] =='Person' or j['name']=='Man' or j['name']=='Woman' or j['name']=='Human'):
            person_count =person_count +1
        if (j['name'] =='Helmet'):
            hat_count=hat_count+1
            
    if (person_count!=hat_count):
        no_match_list.append(i.name)
        

print ("Number of persons found in images:", person_count,"\n")
print ("Number of hardhats found in images:", hat_count, "\n")
print ("Number of images processed:", image_counter, "\n")     
print ("Names of images where hat count is not equal to total number of persons:\n")

for i in no_match_list:
    i=re.sub(final_prefix,'',i)
    i=re.sub('.json','',i)
    print(i)
```
Follow below steps to run Python SDK:

1. Download python code

Download [code](./python-script/pythonscript.py) file and save it your directory.

2. Update variables

Open the python script and update all of the below variables. 

Hint:
The "namespace_name" can be found by navigating to the OCI console, selecting your Profile, selecting your tenancy, and finding "Object Storage Namespace".
The "bucket_name" should be set to "pidaydemo".
The "input_prefix" should be set to "sample-images". 

```Python
namespace_name = "<namespace name>"
bucket_name = "<bucket name>"
compartment_id = "<compartment id>"
input_prefix = "<folder name for images>"
output_prefix = "<output folder name for results>"
```

3. Execute the code
Navigate to the directory where you saved the above file (by default, it should be in the 'Downloads' folder) using your terminal and execute the file by running:
```
python pythonscript.py
```

4. Result
You will see the following results:

``Number of persons found in images: XX``

``Number of hardhats found in images: XX``

``Number of images processed: XX``

``Number of images where hat count is not equal to total number of persons:``



## Learn More
To know more about the Python SDK visit [Python OCI-Vision](https://docs.oracle.com/en-us/iaas/tools/python/2.58.0/api/ai_vision/client/oci.ai_vision.AIServiceVisionClient.html)

Congratulations on completing this lab!

[Proceed to the next lab](#next).
