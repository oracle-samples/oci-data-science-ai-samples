package com.company;
import com.oracle.bmc.ConfigFileReader;
import com.oracle.bmc.auth.AuthenticationDetailsProvider;
import com.oracle.bmc.auth.ConfigFileAuthenticationDetailsProvider;
import com.oracle.bmc.ailanguage.AIServiceLanguageClient;
import com.oracle.bmc.ailanguage.model.*;
import com.oracle.bmc.ailanguage.requests.*;
import com.oracle.bmc.ailanguage.responses.*;

import java.io.IOException;

public class Main {

    public static void main(String[] args) {
        try {
            /* Step 1: Just reading a config file with my credentials so the application acts on my behalf */
            final ConfigFileReader.ConfigFile configFile =
                    ConfigFileReader.parse("C:\\Users\\lecabrer\\.oci\\config", "DEFAULT");
            final AuthenticationDetailsProvider provider =
                    new ConfigFileAuthenticationDetailsProvider(configFile);

            /* Step 2: Create a service client */
            AIServiceLanguageClient client = new AIServiceLanguageClient(provider);

            /* Step 3: Create a request and dependent object(s). */
            DetectDominantLanguageDetails detectdominantLanguageDetails =
                    DetectDominantLanguageDetails.builder()
                    .text("Este es un texto en el idioma de mi madre, la mejor mamá del mundo.").build();

            DetectDominantLanguageRequest detectDominantLanguageRequest = DetectDominantLanguageRequest.builder()
                    .detectDominantLanguageDetails(detectdominantLanguageDetails)
                    .opcRequestId("Just-some-unique-id")
                    .build();

            /* Step 4: Send request to the Client */
            DetectDominantLanguageResponse response = client.
                    detectDominantLanguage(detectDominantLanguageRequest);

            System.out.println("Detected language: " +
                            response.getDetectDominantLanguageResult().getLanguages().get(0).getName());
        }
        catch(IOException e) {
            e.printStackTrace();
        }
    }
}
