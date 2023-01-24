package com.company;
import com.oracle.bmc.ConfigFileReader;
import com.oracle.bmc.auth.*;
import com.oracle.bmc.ailanguage.AIServiceLanguageClient;
import com.oracle.bmc.ailanguage.model.*;
import com.oracle.bmc.ailanguage.requests.*;
import com.oracle.bmc.ailanguage.responses.*;


import java.io.IOException;
import java.net.ConnectException;
import java.net.SocketTimeoutException;
import java.util.ArrayList;
import java.util.Arrays;

public class Main {

    public static void main(String[] args) {
        try {

            /* Step 1: Authentication */
            AuthenticationDetailsProvider provider = authenticateWithConfigFile();
            //InstancePrincipalsAuthenticationDetailsProvider provider = authenticateWithServicePrincipal();
            //ResourcePrincipalAuthenticationDetailsProvider provider = authenticateWithResourcePrincipal();
            //AuthenticationDetailsProvider provider = authenticateWithSimpleAuthentication();

            /* Step 2: Create a service client */
            AIServiceLanguageClient client = AIServiceLanguageClient.builder().build(provider);

            /* Step 3: Sample of single record API */
            DetectDominantLanguageDetails detectdominantLanguageDetails =
                    DetectDominantLanguageDetails.builder()
                    .text("Este es un texto en el idioma de mi madre, la mejor mamá del mundo.").build();

            DetectDominantLanguageRequest detectDominantLanguageRequest = DetectDominantLanguageRequest.builder()
                    .detectDominantLanguageDetails(detectdominantLanguageDetails)
                    .opcRequestId("Just-some-unique-id")
                    .build();

            DetectDominantLanguageResponse response = client.
                    detectDominantLanguage(detectDominantLanguageRequest);

            System.out.println("Detected language: " +
                            response.getDetectDominantLanguageResult().getLanguages().get(0).getName());


            /* Step 4: Sample using more efficient batch APIs */
            BatchLanguageTranslationDetails batchLanguageTranslationDetails = BatchLanguageTranslationDetails.builder()
                    .targetLanguageCode("en")
                    .documents(new ArrayList<>(Arrays.asList(TextDocument.builder()
                            .key("key1")
                            .text("El idioma español es muy facil de aprender.")
                            .languageCode("es").build()))).build();

            BatchLanguageTranslationRequest batchLanguageTranslationRequest = BatchLanguageTranslationRequest.builder()
                    .batchLanguageTranslationDetails(batchLanguageTranslationDetails)
                    .opcRequestId("EMFIG6AAEBVTRXALWQTC<unique_ID>").build();

            /* Send request to the Client */
            BatchLanguageTranslationResponse response1 = client.batchLanguageTranslation(batchLanguageTranslationRequest);
            System.out.println("Translation: " + response1.getBatchLanguageTranslationResult().getDocuments().get(0).getTranslatedText());


        }
        catch(IOException e) {
            e.printStackTrace();
        }
    }

    //https://github.com/oracle/oci-java-sdk/blob/master/bmc-examples/src/main/java/AuthenticationPolicyExample.java
    // Configuring the AuthenticationDetailsProvider. It's assuming there is a default OCI
    // config file
    // "~/.oci/config", and a profile in that config with the name "DEFAULT". Make changes to
    // the following
    // line if needed and use ConfigFileReader.parse(configurationFilePath, profile);
    private static AuthenticationDetailsProvider authenticateWithConfigFile() throws IOException {
        try {
            // Uncomment below line and provide config file path if your config file is not at default location "~/.oci/config"
            // final ConfigFileReader.ConfigFile configFile =
            //          ConfigFileReader.parse("<PATH TO YOUR CONFIG FILE>", "DEFAULT");
            // final AuthenticationDetailsProvider provider = new ConfigFileAuthenticationDetailsProvider(configFile);

            return new ConfigFileAuthenticationDetailsProvider("DEFAULT");
        } catch (Exception e) {
            e.printStackTrace();
            throw e;
        }
    }

    //Using Instance Principal
    //https://github.com/oracle/oci-java-sdk/blob/master/bmc-examples/src/main/java/InstancePrincipalsAuthenticationDetailsProviderExample.java
    private static InstancePrincipalsAuthenticationDetailsProvider authenticateWithServicePrincipal() {
        final InstancePrincipalsAuthenticationDetailsProvider provider;
        try {
            provider = InstancePrincipalsAuthenticationDetailsProvider.builder().build();
            return provider;
        } catch (Exception e) {
            if (e.getCause() instanceof SocketTimeoutException
                    || e.getCause() instanceof ConnectException) {
                System.out.println(
                        "This sample only works when running on an OCI instance. Are you sure you’re running on an OCI instance? For more info see: https://docs.cloud.oracle.com/Content/Identity/Tasks/callingservicesfrominstances.htm");
                return null;
            }
            throw e;
        }
    }

    //https://github.com/oracle/oci-java-sdk/blob/master/bmc-examples/src/main/java/FunctionsEphemeralResourcePrincipalAuthenticationDetailsProviderExample.java
    //Using Resource Principal
    private static ResourcePrincipalAuthenticationDetailsProvider authenticateWithResourcePrincipal() {
        return ResourcePrincipalAuthenticationDetailsProvider.builder().build();
    }

    //https://github.com/oracle/oci-java-sdk/blob/master/bmc-examples/src/main/java/SimpleAuthenticationDetailsProviderExample.java
    //SimpleAuthenticationDetailsProvider
    private static AuthenticationDetailsProvider authenticateWithSimpleAuthentication(String[] args) {
        if (args.length != 5) {
            throw new IllegalArgumentException(
                    "This example expects five arguments: tenantId, userId, fingerprint, privateKey and passPhrase");
        }

        final String tenantId = args[0];
        final String userId = args[1];
        final String fingerprint = args[2];
        final String privateKey = args[3];
        final String passPhrase = args[4];

        return SimpleAuthenticationDetailsProvider.builder()
                .tenantId(tenantId)
                .userId(userId)
                .fingerprint(fingerprint)
                .privateKeySupplier(new StringPrivateKeySupplier(privateKey))
                .passPhrase(passPhrase)
                .build();
    }
}
