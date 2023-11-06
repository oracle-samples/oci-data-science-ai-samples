# OCI Language: Getting Started with the Java SDK

## Introduction

Oracle Cloud Infrastructure provides a number of Software Development Kits (SDKs) to facilitate development of custom solutions. SDKs allow you to build and deploy apps that integrate with Oracle Cloud Infrastructure services. Each SDK also includes tools and artifacts you need to develop an app, such as code samples and documentation. In addition, if you want to contribute to the development of the SDKs, they are all open source and available on GitHub.

You can invoke OCI Language capabilities through the OCI SDKs.

## Pre-requisites

### Get the libraries

Download and install the OCI Java SDK so you have access to the libraries you need to use, as described in [this article](https://docs.oracle.com/en-us/iaas/Content/API/SDKDocs/javasdkgettingstarted.htm). 

For the sample in this directory, I relied on Maven get the libraries I needed:  **oci-java-sdk-ailanguage**, **oci-java-sdk-common** and **oci-java-sdk-common-httpclient-jersey**. This is what the dependencies sections looked like in my [pom.xml](pom.xml):

```xml
 <dependencies>
    <dependency>
        <groupId>com.oracle.oci.sdk</groupId>
        <artifactId>oci-java-sdk-ailanguage</artifactId>
        <version>LATEST</version>
    </dependency>
    <dependency>
        <groupId>com.oracle.oci.sdk</groupId>
        <artifactId>oci-java-sdk-common</artifactId>
        <version>LATEST</version>
    </dependency>
    <dependency>
        <!-- Since this is the "application" pom.xml, we do want to
             choose the httpclient to use. -->
        <groupId>com.oracle.oci.sdk</groupId>
        <artifactId>oci-java-sdk-common-httpclient-jersey</artifactId>
        <version>LATEST</version>
    </dependency>
</dependencies>
```

And this is what the imports looked like:

```java
    import com.oracle.bmc.ConfigFileReader;
    import com.oracle.bmc.auth.AuthenticationDetailsProvider;
    import com.oracle.bmc.auth.ConfigFileAuthenticationDetailsProvider;
    import com.oracle.bmc.ailanguage.AIServiceLanguageClient;
    import com.oracle.bmc.ailanguage.model.*;
    import com.oracle.bmc.ailanguage.requests.*;
    import com.oracle.bmc.ailanguage.responses.*;
```

### Authentication

In order for your local code to have the rights to use your OCI services, it needs to have the privileges to do so either by having an instance principal, or act on behalf of a user (by reading a configuration file with the users credentials).  These two topics have been discussed at large in this previous [Java Magazine article](https://blogs.oracle.com/javamagazine/post/first-steps-with-oracle-cloud-infrastructure-sdk-for-java), so I will not repeat the concepts. In the sample, we are simply pointing to a .oci/config file.

```java
            /* Step 1: Just reading a config file with my credentials so the application acts on my behalf */
            
            final ConfigFileReader.ConfigFile configFile =
                ConfigFileReader.parse("C:\\...path to your file...\\.oci\\config", "DEFAULT");
            final AuthenticationDetailsProvider provider =
                new ConfigFileAuthenticationDetailsProvider(configFile);
```

OCI SDK provides some other Authentication methods as well and sample for these methods can found below in links below.
* Instance Principal Authentication - https://github.com/oracle/oci-java-sdk/blob/master/bmc-examples/src/main/java/InstancePrincipalsAuthenticationDetailsProviderExample.java
* Resource Principal Authentication - https://github.com/oracle/oci-java-sdk/blob/master/bmc-examples/src/main/java/FunctionsEphemeralResourcePrincipalAuthenticationDetailsProviderExample.java
* Simple Authentication - https://github.com/oracle/oci-java-sdk/blob/master/bmc-examples/src/main/java/SimpleAuthenticationDetailsProviderExample.java

## Using OCI Language from Java

Essentially, we just need to create a language client to issue the calls, prepare a request with its dependent object, and then send a request to the client, as shown in Steps 2,3 and 4 in the [Java sample code](https://github.com/oracle/oci-data-science-ai-samples/tree/master/ai_services/language/java/src/main/java/com/company).

```java    
            /* Step 2: Create a service client */
            AIServiceLanguageClient client = new AIServiceLanguageClient(provider);

            /* Step 3: Create a request and dependent object(s). */
            DetectDominantLanguageDetails detectdominantLanguageDetails =
                    DetectDominantLanguageDetails.builder()
                    .text("Este es un texto en el idioma de mi madre, la mejor mamá del mundo.").build();

            DetectDominantLanguageRequest detectDominantLanguageRequest =
                    DetectDominantLanguageRequest.builder()
                    .detectDominantLanguageDetails(detectdominantLanguageDetails)
                    .opcRequestId("Just-some-unique-id")
                    .build();

            /* Step 4: Send request to the Client */
            DetectDominantLanguageResponse response = client.
                    detectDominantLanguage(detectDominantLanguageRequest);
```

In this specific case, we are simply detecting the language of the provided text, but you can follow the same pattern to use the rest of the OCI Language capabilities.  For instance, you may want to identify named entities or sentiment a set of records, or automatically classify text. Thanks to AI Services you can leverage the power of AI without having to have a background in data science or natural language processing.

## Additional Resources
[OCI Language self-paced workshop](https://apexapps.oracle.com/pls/apex/dbpm/r/livelabs/workshop-attendee-2?p210_workshop_id=887&p210_type=1&session=117554425341659)

[OCI Language documentation](https://docs.oracle.com/en-us/iaas/language/using/language.htm)

[OCI SDK for Java](https://docs.oracle.com/en-us/iaas/Content/API/SDKDocs/javasdk.htm#SDK_for_Java)

[Language API General Reference](https://docs.oracle.com/en-us/iaas/api/#/en/language/20210101/)

[Language API Java Specific Reference](https://docs.oracle.com/en-us/iaas/tools/java/2.13.1/com/oracle/bmc/ailanguage/AIServiceLanguage.html)
