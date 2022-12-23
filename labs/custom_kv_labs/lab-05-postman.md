# Lab 5: Call your model through REST API using Postman
## Introduction

In this lab, we will use Document Services in Postman.

Estimated Time: 15 minutes


### Objectives

In this workshop, you will:

* Learn how to call the model using REST API calls through postman

### Prerequisites:

* Basic knowledge of REST API calls.
* Postman GUI in your local setup. If you don't have POSTMAN, please download it from [POSTMAN](https://www.postman.com/downloads/)

## TASK 1: Setting Up Postman for OCI Document Service REST APIs

* Visit the OCI Postman workspace and login with your credentials.
* Fork the Document Understanding API collection in your workspace by navigating to Document Understanding API collection and clicking the "Fork" option.
![](./custom_kv_labs/images/postman1.PNG)
* Enter name to identify forked Document Understanding API collection, select the workspace you want to fork the collection to and click "Fork Collection".
![](./custom_kv_labs/images/postman2.PNG)
* Fork the OCI Credentials Environment in your workspace by navigating to Environments and clicking the "Fork" option.
![](./custom_kv_labs/images/postman3.PNG)
* Enter name to identify forked OCI credentials environment, select the workspace you want to fork the collection to and click "Fork Collection".
![](./custom_kv_labs/images/postman4.PNG)
* Navigate to your workspace and open newly forked environment (OCI Credentials), and set the variables tenancyId, authUserId, keyFingerprint and private Key. These are same that are found in the .oci file you created in the Lab 4 (Task 2). Make sure to set both Initial Value and Current Value of the variables(set both as the same value).Click the Save button to commit your changes to the environment.
![](./custom_kv_labs/images/postman5.PNG)


## TASK 2: Invoke Document Understanding OCI REST APIs

* Navigate to "Create a processor job for document analysis" section under "processor Jobs"
![](./custom_kv_labs/images/request1.PNG)
* Update the base url with "https://document.aiservice.{region}.oci.oraclecloud.com/20221109" and region being the one in which model is created.

  (sample url: https://document.aiservice.us-ashburn-1.oci.oraclecloud.com/20221109/processorJobs)
![](./custom_kv_labs/images/request2.PNG)
* Navigate to "raw" under "body" section to enter the payload for request. Change the format to "JSON"
![](./custom_kv_labs/images/request3.PNG)
* Edit the payload given below according to your model ID, data(in inputLocation), outputLocation and compartment ID

  (Note: data should be base64 encoded)
  ```
  {
    "processorConfig": {
      "processorType": "GENERAL",
        "features": [
          {
            "featureType": "KEY_VALUE_EXTRACTION",
            "modelId": <model_id>
          }
        ]
      },
    "inputLocation": {
      "sourceType": "INLINE_DOCUMENT_CONTENT",
      "data": <base64 encoded document>
    },
    "outputLocation": {
      "bucketName": <name of the bucket>,
      "namespaceName": <namespace under which model exists>,
      "prefix": "prefix"
    },
    "compartmentId": <ID of compartment where the model is created>
  }
  ```

* Enter the payload in the postman and click on send. In the response "lifecycleState" should be in SUCCEEDED state.
![](./custom_kv_labs/images/request4.PNG)
* The output JSON file can be found in the output location specified by user
