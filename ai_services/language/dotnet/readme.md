# OCI Language: Getting Started with the .Net SDK

## Introduction

Oracle Cloud Infrastructure provides a number of Software Development Kits (SDKs) to facilitate development of custom solutions. SDKs allow you to build and deploy apps that integrate with Oracle Cloud Infrastructure services. Each SDK also includes tools and artifacts you need to develop an app, such as code samples and documentation. In addition, if you want to contribute to the development of the SDKs, they are all open source and available on GitHub.

You can invoke OCI Language capabilities through the OCI SDKs.

## Pre-requisites:

### Set up config file

You need to set up an API Signing Key and a configuration file so that the SDK can find  the credentials needed to connect to your OCI tenancy and used the Language capabilities.

If you have never done this before, you may want to follow the steps described in the [OCI Language Workshop - Lab 3 > Task 2](https://apexapps.oracle.com/pls/apex/dbpm/r/livelabs/workshop-attendee-2?p210_workshop_id=887&p210_type=3&session=106800683771485).

Other related documents:
* [Generating API key](https://docs.oracle.com/en-us/iaas/Content/API/Concepts/apisigningkey.htm)
* [SDK and CLI configuration file](https://docs.oracle.com/en-us/iaas/Content/API/Concepts/sdkconfig.htm#SDK_and_CLI_Configuration_File)


### .Net requirements

Any project you create needs to have the following libraries -- which you can install using the Nuget package manager:
 
 * [OCI.DotNetSDK.Common](https://www.nuget.org/packages/OCI.DotNetSDK.Common/)
 * [OCI.DotNetSDK.Ailanguage](https://www.nuget.org/packages/OCI.DotNetSDK.Ailanguage/)

## Projects in the Language.sln solution

**LanguageBasicDemo.csproj** showcases how to call single record APIs. It contains a thin wrapper library (languagewrapper.cs) that makes it easier to call single record APIs.

