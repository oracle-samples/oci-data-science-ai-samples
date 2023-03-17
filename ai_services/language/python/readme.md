# OCI Language: Getting Started with the Python SDK

## Introduction

Oracle Cloud Infrastructure provides a number of Software Development Kits (SDKs) to facilitate development of custom solutions. SDKs allow you to build and deploy apps that integrate with Oracle Cloud Infrastructure services. Each SDK also includes tools and artifacts you need to develop an app, such as code samples and documentation. In addition, if you want to contribute to the development of the SDKs, they are all open source and available on GitHub.

You can invoke OCI Language capabilities through the OCI SDKs.

## Pre-requisites:

### Set up config file

You need to set up an API Signing Key and a configuration file so that the SDK can find  the credentials needed to connect to your OCI tenancy and used the Language capabilities.

If you have never done this before, you may want to follow the steps described in the [OCI Language Workshop - Lab 3 > Task 2](https://apexapps.oracle.com/pls/apex/dbpm/r/livelabs/workshop-attendee-2?p210_workshop_id=887&p210_type=3&session=106800683771485).

Other related documents:
* [Generating API KEY](https://docs.oracle.com/en-us/iaas/Content/API/Concepts/apisigningkey.htm)
* [SDK and CLI Configuration File](https://docs.oracle.com/en-us/iaas/Content/API/Concepts/sdkconfig.htm#SDK_and_CLI_Configuration_File)


### Python requirements

Make sure you have Python 3.x version and that it’s available from your command line. You can check this by simply running 

> python --version

If you do not have Python, please install the latest 3.x version from python.org

Additionally, you’ll need to make sure you have pip available. You can check this by running:

> pip --version

If you installed Python from source, with an installer from python.org, or via Homebrew you should already have pip. If you’re on Linux and installed using your OS package manager, you may have to install pip separately.

### Set up and activate a virtual environment 

To create a virtual environment, run the venv module as a script as shown below

> python3 -m venv <name of virtual environment>

Once you’ve created a virtual environment, you may activate it.

In Mac OS / Linux:

> source \<name of virtual environment>/bin/activate

In Windows:

> \<name of virtual environment>\Scripts\activate

### Install OCI SDK

Once you have activated your environment, install the OCI SDK by running:

> pip install oci


## Samples

**languagebasicdemo.py** showcases how to call single record APIs.

**languagebatchdemo.py** reads a set of reviews from a CSV file with reviews, uses batching API to do aspect based sentiment analysis and outputs a CSV for all the sentiments found. This is a good example on how to call batch APIs efficiently. 

**languageBatchSamples.py** showcases how to call Batch record APIs.

**languageCustomNERSample.py** showcase creating and training of Named entity recognition custom model

**languageCustomTXTCSample.py** showcase creating and training of Text classification custom model

**languageTranslation.py** showcase text translation.