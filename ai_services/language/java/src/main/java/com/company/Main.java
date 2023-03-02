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
import java.util.List;
import java.util.stream.Collectors;

public class Main {

    private static AIServiceLanguageClient client;

    public static void main(String[] args) {
        try {
            String text = "Zoom interface is really simple and easy to use. The learning curve is very short thanks to the interface. It is very easy to share the Zoom link to join the video conference. Screen sharing quality is just ok. Zoom now claims to have 300 million meeting participants per day. It chose Oracle Corporation co-founded by Larry Ellison and headquartered in Redwood Shores , for its cloud infrastructure deployments over the likes of Amazon, Microsoft, Google, and even IBM to build an enterprise grade experience for its product. The security feature is significantly lacking as it allows people to zoom bomb";
            String englishLanguageCode = "en";

            Main aiServiceLanguageExample = new Main();

            /* Step 1: Authentication */
            AuthenticationDetailsProvider provider = aiServiceLanguageExample.authenticateWithConfigFile();
            //InstancePrincipalsAuthenticationDetailsProvider provider = aiServiceLanguageExample.authenticateWithServicePrincipal();
            //ResourcePrincipalAuthenticationDetailsProvider provider = aiServiceLanguageExample.authenticateWithResourcePrincipal();
            //AuthenticationDetailsProvider provider = aiServiceLanguageExample.authenticateWithSimpleAuthentication(args);

            /* Step 2: Create a service client */
            client = AIServiceLanguageClient.builder().build(provider);

            /* Single Documents APIs */
            DetectLanguageSentimentsResult sentimentsResult = aiServiceLanguageExample.getLanguageSentiments(text);
            DetectLanguageEntitiesResult entitiesResult = aiServiceLanguageExample.getLanguageEntities(text);
            DetectDominantLanguageResult dominantLanguageResult = aiServiceLanguageExample.getDominantLanguage(text);
            DetectLanguageKeyPhrasesResult keyPhrasesResult = aiServiceLanguageExample.getLanguageKeyPhrases(text);
            DetectLanguageTextClassificationResult textClassificationResult = aiServiceLanguageExample.getLanguageTextClassification(text);

            aiServiceLanguageExample.printSentiments(sentimentsResult);
            aiServiceLanguageExample.printEntities(entitiesResult);
            aiServiceLanguageExample.printLanguageType(dominantLanguageResult);
            aiServiceLanguageExample.printKeyPhrases(keyPhrasesResult);
            aiServiceLanguageExample.printTextClassification(textClassificationResult);

            /* Sample using more efficient batch APIs */
            getTranslatedText("El idioma español es muy facil de aprender.", "es", "en");
            BatchDetectLanguageSentimentsResult batchSentimentsResult = aiServiceLanguageExample.getLanguageBatchSentiments(text, englishLanguageCode);
            BatchDetectLanguageEntitiesResult batchEntitiesResult = aiServiceLanguageExample.getLanguageBatchEntities(text, englishLanguageCode);
            BatchDetectDominantLanguageResult batchDominantLanguageResult = aiServiceLanguageExample.getBatchDominantLanguage(text);
            BatchDetectLanguageKeyPhrasesResult batchKeyPhrasesResult = aiServiceLanguageExample.getLanguageBatchKeyPhrases(text, englishLanguageCode);
            BatchDetectLanguageTextClassificationResult batchTextClassificationResult = aiServiceLanguageExample.getLanguageBatchTextClassification(text, englishLanguageCode);

            aiServiceLanguageExample.printBatchSentiments(batchSentimentsResult);
            aiServiceLanguageExample.printBatchEntities(batchEntitiesResult);
            aiServiceLanguageExample.printBatchLanguageType(batchDominantLanguageResult);
            aiServiceLanguageExample.printBatchKPE(batchKeyPhrasesResult);
            aiServiceLanguageExample.printBatchTextClass(batchTextClassificationResult);

            client.close();

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
    private AuthenticationDetailsProvider authenticateWithConfigFile() throws IOException {
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
    private InstancePrincipalsAuthenticationDetailsProvider authenticateWithServicePrincipal() {
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
    private ResourcePrincipalAuthenticationDetailsProvider authenticateWithResourcePrincipal() {
        return ResourcePrincipalAuthenticationDetailsProvider.builder().build();
    }

    //https://github.com/oracle/oci-java-sdk/blob/master/bmc-examples/src/main/java/SimpleAuthenticationDetailsProviderExample.java
    //SimpleAuthenticationDetailsProvider
    private AuthenticationDetailsProvider authenticateWithSimpleAuthentication(String[] args) {
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

    private BatchDetectLanguageSentimentsResult getLanguageBatchSentiments(String text, String languageCode) {
        TextDocument sentimentsDocument = TextDocument.builder().key("doc1").text(text).languageCode(languageCode).build();
        java.util.List<TextDocument> documents = Arrays.asList(sentimentsDocument);
        BatchDetectLanguageSentimentsDetails sentimentsDetails = BatchDetectLanguageSentimentsDetails
                .builder()
                .documents(documents)
                .build();
        BatchDetectLanguageSentimentsRequest request = BatchDetectLanguageSentimentsRequest
                .builder()
                .batchDetectLanguageSentimentsDetails(sentimentsDetails)
                .build();
        BatchDetectLanguageSentimentsResponse response = client.batchDetectLanguageSentiments(request);
        return response.getBatchDetectLanguageSentimentsResult();
    }

    private BatchDetectLanguageKeyPhrasesResult getLanguageBatchKeyPhrases(String text, String languageCode) {
        TextDocument keyPhraseDocument = TextDocument.builder().key("doc1").text(text).languageCode(languageCode).build();
        java.util.List<TextDocument> documents = Arrays.asList(keyPhraseDocument);
        BatchDetectLanguageKeyPhrasesDetails keyPhrasesDetails = BatchDetectLanguageKeyPhrasesDetails.builder().documents(documents).build();
        BatchDetectLanguageKeyPhrasesRequest request = BatchDetectLanguageKeyPhrasesRequest.builder().batchDetectLanguageKeyPhrasesDetails(keyPhrasesDetails).build();
        BatchDetectLanguageKeyPhrasesResponse response = client.batchDetectLanguageKeyPhrases(request);
        return response.getBatchDetectLanguageKeyPhrasesResult();
    }

    private BatchDetectLanguageTextClassificationResult getLanguageBatchTextClassification(String text, String languageCode) {
        TextDocument textClassificationDocument = TextDocument.builder().key("doc1").text(text).languageCode(languageCode).build();
        java.util.List<TextDocument> documents = Arrays.asList(textClassificationDocument);
        BatchDetectLanguageTextClassificationDetails textClassificationDetails = BatchDetectLanguageTextClassificationDetails.builder().documents(documents).build();
        BatchDetectLanguageTextClassificationRequest request = BatchDetectLanguageTextClassificationRequest.builder().batchDetectLanguageTextClassificationDetails(textClassificationDetails).build();
        BatchDetectLanguageTextClassificationResponse response = client.batchDetectLanguageTextClassification(request);
        return response.getBatchDetectLanguageTextClassificationResult();
    }

    private BatchDetectLanguageEntitiesResult getLanguageBatchEntities(String text, String languageCode) {
        TextDocument entityDocument = TextDocument.builder().key("doc1").text(text).languageCode(languageCode).build();
        java.util.List<TextDocument> documents = Arrays.asList(entityDocument);
        BatchDetectLanguageEntitiesDetails entitiesDetails = BatchDetectLanguageEntitiesDetails.builder().documents(documents).build();
        BatchDetectLanguageEntitiesRequest request = BatchDetectLanguageEntitiesRequest.builder().batchDetectLanguageEntitiesDetails(entitiesDetails).build();
        BatchDetectLanguageEntitiesResponse response = client.batchDetectLanguageEntities(request);
        return response.getBatchDetectLanguageEntitiesResult();
    }

    private BatchDetectDominantLanguageResult getBatchDominantLanguage(String text) {
        DominantLanguageDocument dominantLanguageDocument = DominantLanguageDocument.builder().key("doc1").text(text).build();
        java.util.List<DominantLanguageDocument> documents = Arrays.asList(dominantLanguageDocument);
        BatchDetectDominantLanguageDetails dominantLanguageDetails = BatchDetectDominantLanguageDetails.builder().documents(documents).build();
        BatchDetectDominantLanguageRequest request = BatchDetectDominantLanguageRequest.builder().batchDetectDominantLanguageDetails(dominantLanguageDetails).build();
        BatchDetectDominantLanguageResponse response = client.batchDetectDominantLanguage(request);
        return response.getBatchDetectDominantLanguageResult();
    }

    private DetectLanguageSentimentsResult getLanguageSentiments(String text) {
        DetectLanguageSentimentsDetails sentimentsDetails = DetectLanguageSentimentsDetails.builder().text(text).build();
        DetectLanguageSentimentsRequest request = DetectLanguageSentimentsRequest.builder().detectLanguageSentimentsDetails(sentimentsDetails).build();
        DetectLanguageSentimentsResponse response = client.detectLanguageSentiments(request);
        return response.getDetectLanguageSentimentsResult();
    }

    private DetectLanguageEntitiesResult getLanguageEntities(String text) {
        DetectLanguageEntitiesDetails entitiesDetails = DetectLanguageEntitiesDetails.builder().text(text).build();
        DetectLanguageEntitiesRequest request = DetectLanguageEntitiesRequest.builder().detectLanguageEntitiesDetails(entitiesDetails).build();
        DetectLanguageEntitiesResponse response = client.detectLanguageEntities(request);
        return response.getDetectLanguageEntitiesResult();
    }

    private DetectDominantLanguageResult getDominantLanguage(String text) {
        DetectDominantLanguageDetails languageDetails = DetectDominantLanguageDetails.builder().text(text).build();
        DetectDominantLanguageRequest request = DetectDominantLanguageRequest.builder().detectDominantLanguageDetails(languageDetails).build();
        DetectDominantLanguageResponse response = client.detectDominantLanguage(request);
        return response.getDetectDominantLanguageResult();
    }

    private DetectLanguageKeyPhrasesResult getLanguageKeyPhrases(String text) {
        DetectLanguageKeyPhrasesDetails keyPhrasesDetails = DetectLanguageKeyPhrasesDetails.builder().text(text).build();
        DetectLanguageKeyPhrasesRequest request = DetectLanguageKeyPhrasesRequest.builder().detectLanguageKeyPhrasesDetails(keyPhrasesDetails).build();
        DetectLanguageKeyPhrasesResponse response = client.detectLanguageKeyPhrases(request);
        return response.getDetectLanguageKeyPhrasesResult();
    }

    private DetectLanguageTextClassificationResult getLanguageTextClassification(String text) {
        DetectLanguageTextClassificationDetails textClassificationDetails = DetectLanguageTextClassificationDetails.builder().text(text).build();
        DetectLanguageTextClassificationRequest request = DetectLanguageTextClassificationRequest.builder().detectLanguageTextClassificationDetails(textClassificationDetails).build();
        DetectLanguageTextClassificationResponse response = client.detectLanguageTextClassification(request);
        return response.getDetectLanguageTextClassificationResult();
    }

    private static void getTranslatedText(String text, String sourceLanguageCoce, String targetLanguageCode) {
        BatchLanguageTranslationDetails batchLanguageTranslationDetails = BatchLanguageTranslationDetails.builder()
                .targetLanguageCode(targetLanguageCode)
                .documents(new ArrayList<>(Arrays.asList(TextDocument.builder()
                        .key("key1")
                        .text(text)
                        .languageCode(sourceLanguageCoce).build()))).build();

        BatchLanguageTranslationRequest batchLanguageTranslationRequest = BatchLanguageTranslationRequest.builder()
                .batchLanguageTranslationDetails(batchLanguageTranslationDetails)
                .opcRequestId("EMFIG6AAEBVTRXALWQTC<unique_ID>").build();

        BatchLanguageTranslationResponse response1 = client.batchLanguageTranslation(batchLanguageTranslationRequest);
        System.out.println("Translation: " + response1.getBatchLanguageTranslationResult().getDocuments().get(0).getTranslatedText());
    }

    private void printBatchSentiments(BatchDetectLanguageSentimentsResult result) {
        if (result.getDocuments() != null && result.getDocuments().size() > 0) {
            SentimentDocumentResult documentResult = result.getDocuments().get(0);
            List<SentimentAspect> aspects = documentResult.getAspects();
            String printFormat = "%s [%s - %s]";
            System.out.println();
            System.out.println("========= Language Batch Aspect Based Sentiment ========");
            aspects.forEach(aspect -> System.out.println(String.format(printFormat, aspect.getText(), aspect.getSentiment(), aspect.getScores())));
            System.out.println("========= End ========");
            System.out.println();
        }

        if (result.getErrors() != null && result.getErrors().size() > 0) {
            System.out.println("========= Language Batch Aspect Based Sentiment Error========");
            System.out.println(result.getErrors().get(0).getError().getMessage());
            System.out.println("========= End ========");
        }
    }

    private void printBatchEntities(BatchDetectLanguageEntitiesResult result) {
        if (result.getDocuments() != null && result.getDocuments().size() > 0) {
            EntityDocumentResult documentResult = result.getDocuments().get(0);
            List<HierarchicalEntity> entities = documentResult.getEntities();
            String printFormat = "%s [%s]";
            System.out.println("========= Batch Entities ========");
            entities.forEach(entity -> System.out.println(String.format(printFormat, entity.getText(), entity.getType())));
            System.out.println("========= End ========");
            System.out.println();
        }

        if (result.getErrors() != null && result.getErrors().size() > 0) {
            System.out.println("========= Language Batch Entity Error========");
            System.out.println(result.getErrors().get(0).getError().getMessage());
            System.out.println("========= End ========");
        }
    }

    private void printBatchKPE(BatchDetectLanguageKeyPhrasesResult result) {
        if (result.getDocuments() != null && result.getDocuments().size() > 0) {
            KeyPhraseDocumentResult documentResult = result.getDocuments().get(0);
            List<KeyPhrase> keyPhrases = documentResult.getKeyPhrases();
            System.out.println("========= Language Batch Key Phrases ========");
            List<String> keyPhrasesStr = keyPhrases.stream().map(keyPhrase -> keyPhrase.getText()+ " ("+keyPhrase.getScore()+")").collect(Collectors.toList());
            System.out.println(String.join(",", keyPhrasesStr));
            System.out.println("========= End ========");
            System.out.println();
        }

        if (result.getErrors() != null && result.getErrors().size() > 0) {
            System.out.println("========= Language Batch Key Phrases Error========");
            System.out.println(result.getErrors().get(0).getError().getMessage());
            System.out.println("========= End ========");
        }
    }

    private void printBatchTextClass(BatchDetectLanguageTextClassificationResult result) {
        if (result.getDocuments() != null && result.getDocuments().size() > 0) {
            TextClassificationDocumentResult documentResult = result.getDocuments().get(0);
            List<TextClassification> textClassifications = documentResult.getTextClassification();
            String printFormat = "%s (%s)";
            System.out.println("========= Language Batch Text Classification ========");
            textClassifications.forEach(textClassification -> System.out.println(String.format(printFormat, textClassification.getLabel(), textClassification.getScore())));
            System.out.println("========= End ========");
            System.out.println();
        }

        if (result.getErrors() != null && result.getErrors().size() > 0) {
            System.out.println("========= Language Batch Text Classification Error========");
            System.out.println(result.getErrors().get(0).getError().getMessage());
            System.out.println("========= End ========");
        }
    }

    private void printBatchLanguageType(BatchDetectDominantLanguageResult result) {
        if (result.getDocuments() != null && result.getDocuments().size() > 0) {
            DominantLanguageDocumentResult documentResult = result.getDocuments().get(0);
            List<DetectedLanguage> languages = documentResult.getLanguages();
            System.out.println("========= Batch Dominant Language ========");
            List<String> languagesStr = languages.stream().map(language -> language.getName()+ " ("+language.getScore()+")").collect(Collectors.toList());
            System.out.println(String.join(",", languagesStr));
            System.out.println("========= End ========");
            System.out.println();
        }

        if (result.getErrors() != null && result.getErrors().size() > 0) {
            System.out.println("========= Batch Dominant Language Error========");
            System.out.println(result.getErrors().get(0).getError().getMessage());
            System.out.println("========= End ========");
        }
    }

    private void printSentiments(DetectLanguageSentimentsResult result) {
        List<SentimentAspect> aspects = result.getAspects();
        String printFormat = "%s [%s - %s]";

        System.out.println();
        System.out.println("========= Language Aspect Based Sentiment ========");
        aspects.forEach(aspect -> System.out.println(String.format(printFormat, aspect.getText(), aspect.getSentiment(), aspect.getScores())));
        System.out.println("========= End ========");
        System.out.println();
    }

    private void printEntities(DetectLanguageEntitiesResult result) {
        List<Entity> entities = result.getEntities();
        String printFormat = "%s [%s]";
        System.out.println("========= Entities ========");
        entities.forEach(entity -> System.out.println(String.format(printFormat, entity.getText(), entity.getType())));
        System.out.println("========= End ========");
        System.out.println();
    }

    private void printLanguageType(DetectDominantLanguageResult result) {
        System.out.println("========= Dominant Language ========");
        List<DetectedLanguage> languages = result.getLanguages();
        List<String> languagesStr = languages.stream().map(language -> language.getName()+ " ("+language.getScore()+")").collect(Collectors.toList());
        System.out.println(String.join(",", languagesStr));
        System.out.println("========= End ========");
        System.out.println();
    }

    private void printKeyPhrases(DetectLanguageKeyPhrasesResult result) {
        List<KeyPhrase> keyPhrases = result.getKeyPhrases();
        System.out.println("========= Language Key Phrases ========");
        List<String> keyPhrasesStr = keyPhrases.stream().map(keyPhrase -> keyPhrase.getText()+ " ("+keyPhrase.getScore()+")").collect(Collectors.toList());
        System.out.println(String.join(",", keyPhrasesStr));
        System.out.println("========= End ========");
        System.out.println();
    }

    private void printTextClassification(DetectLanguageTextClassificationResult result) {
        List<TextClassification> textClassifications = result.getTextClassification();
        String printFormat = "%s (%s)";
        System.out.println("========= Language Topic Labels & Related Words ========");
        System.out.println("========= Language Topic Labels ========");
        textClassifications.forEach(textClassification -> System.out.println(String.format(printFormat, textClassification.getLabel(), textClassification.getScore())));
        System.out.println("========= End ========");
    }
}
