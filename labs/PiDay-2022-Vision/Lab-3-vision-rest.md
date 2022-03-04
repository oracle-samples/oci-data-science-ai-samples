# Lab 3: Access OCI Vision with REST APIs

## Introduction


In this lab session, we will show you how to access OCI Vision using POSTMAN.

Postman is a GUI-based REST API invocation tool that is very popular among developers.

*Estimated Lab Time*: 10 minutes

### Objectives:
* Learn how to access Language Service through REST APIs.

### Prerequisites:
* Basic knowledge of REST API calls.
* Postman GUI in your local setup. If you don't have POSTMAN, please download it from [POSTMAN](https://www.postman.com/downloads/)

## **TASK 1:** Setup API Signing Key and Config File
**Prerequisite: Before you generate a key pair, create the .oci directory in your home directory to store the credentials.**

Mac OS / Linux:

```
<copy>mkdir ~/.oci</copy>
```
Windows:
```
<copy>mkdir %HOMEDRIVE%%HOMEPATH%\.oci</copy>
```

Generate an API signing key pair

1. Open User Settings

  Open the Profile menu (User menu icon) and click User Settings.
    ![](./images/userProfileIcon.png " ")

1. Open API Key

  Navigate to API Key and then Click Add API Key.
    ![](./images/addAPIButton.png " ")

1. Generate API Key

  In the dialog, select Generate API Key Pair. Click Download Private Key and save the key to your .oci directory and then click Add.
    ![](./images/genAPI.png " ")



4. Generate Config File

  Copy the values shown on the console.
    ![](./images/conf.png " ")

    Create a config file in the .oci folder and paste the values copied.
    Replace the key_file value with the path of your generated API Key.
    ![](./images/config2.png " ")



To Know more visit [Generating API KEY](https://docs.oracle.com/en-us/iaas/Content/API/Concepts/apisigningkey.htm) and [SDK and CLI Configuration File](https://docs.oracle.com/en-us/iaas/Content/API/Concepts/sdkconfig.htm#SDK_and_CLI_Configuration_File)

## **TASK 2:** Setting Up Postman for OCI REST APIs
We have provided some scripts and steps below that can be used to allow invoking OCI REST APIs through Postman. Please follow the steps in the order described.

1. Import the environment into Postman

Download the [OCI Environment](./files/OCI_Environment.postman_environment.json) and import the environment into Postman using the 'Import' button at the top.
    ![](./images/importENV.png " ")

Make sure to set OCI_Environment as the active environment.
    ![](./images/setActive.png " ")

1. Set the Variables  
Open and edit the newly imported environment (OCI_Environment), and set the variables tenancyId, authUserId, keyFingerprint and private Key. These are same that are found in the .oci file you created above in Task 1->Step4).

Make sure to set both Initial Value and Current Value of the variables(set both as the same value).

Click the Save button to commit your changes to the environment.
    ![](./images/setVar.png " ")

<!-- ### 5. Add Request in OCI REST COLLECTION

Add Request in the OCI REST COLLECTION Folder
![](./images/4.png " ")

Enter Name and click 'Save to OCI REST COLLECTION'
![](./images/5.png " ")

Just make sure that the OCI REST calls are executed as part of the OCI REST COLLECTION, as that collection contains the necessary javascript code to generate OCI's authentication header -->

## **TASK 3:** Invoke Language OCI REST APIs
** @Wes / @Mark - will need you guys to take this part over since I am not familiar with doing this in postman myself.  **

Invoke Language OCI REST APIs by clicking any one of the requests in the OCI REST COLLECTION. Enter the text you want to analyze in the body as shown below:
    ```
    <copy>{
        "text" : "American football was derived from the European games of rugby and soccer. Unlike the game of soccer, however, American football focuses more on passing and catching the ball with the hands as opposed to kicking the ball with the feet. Standard American football field is 120 yards in length and 160 feet in width. They are hash marks on every yards and every 10 yards. American football is quickly become more popular then baseball and fan bases are increasing rapidly. Jerry Rice, Tom Brady and Lawrence Taylor are few top player of this sports."
    }<copy>
    ```

Below in the example shown to invoke Detect Language Service.
    ![](./images/collectionREST.png " ")

OCI Language Service EndPoints for all the services:

```
# Language Detection
https://language.aiservice.us-ashburn-1.oci.oraclecloud.com/20210101/actions/detectDominantLanguage

# Key Phrase Extraction
https://language.aiservice.us-ashburn-1.oci.oraclecloud.com/20210101/actions/detectLanguageKeyPhrases

# Named Entity Recognition
https://language.aiservice.us-ashburn-1.oci.oraclecloud.com/20210101/actions/detectLanguageEntities

# Text Classification
https://language.aiservice.us-ashburn-1.oci.oraclecloud.com/20210101/actions/detectLanguageTextClassification

# Aspect-Based Sentiment Analysis
https://language.aiservice.us-ashburn-1.oci.oraclecloud.com/20210101/actions/detectLanguageSentiments

```

[Proceed to the next lab](#next).
