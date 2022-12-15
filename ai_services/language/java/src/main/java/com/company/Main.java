package com.company;
import com.oracle.bmc.ConfigFileReader;
import com.oracle.bmc.auth.AuthenticationDetailsProvider;
import com.oracle.bmc.auth.ConfigFileAuthenticationDetailsProvider;
import com.oracle.bmc.ailanguage.AIServiceLanguageClient;
import com.oracle.bmc.ailanguage.model.*;
import com.oracle.bmc.ailanguage.requests.*;
import com.oracle.bmc.ailanguage.responses.*;


import java.io.IOException;
import java.util.ArrayList;
import java.util.Arrays;

public class Main {

    public static void main(String[] args) {
        try {
            /* Step 1: Just reading a config file with my credentials so the application acts on my behalf */
            final ConfigFileReader.ConfigFile configFile =
                    ConfigFileReader.parse("<PATH TO YOUR CONFIG FILE>", "DEFAULT");

            final AuthenticationDetailsProvider provider =
                    new ConfigFileAuthenticationDetailsProvider(configFile);

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
}
