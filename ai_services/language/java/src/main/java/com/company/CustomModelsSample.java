package com.company;

import com.oracle.bmc.ConfigFileReader;
import com.oracle.bmc.ailanguage.AIServiceLanguageClient;
import com.oracle.bmc.ailanguage.model.*;
import com.oracle.bmc.ailanguage.requests.*;
import com.oracle.bmc.ailanguage.responses.*;
import com.oracle.bmc.auth.AuthenticationDetailsProvider;
import com.oracle.bmc.auth.ConfigFileAuthenticationDetailsProvider;

import java.io.IOException;
import java.util.Arrays;

public class CustomModelsSample {

    private static final String compartmentId = "<Specify your COMPARTMENT_ID here>";
    private static final String nerModelName = "ailangaugemodelNERModel";
    private static final String txtcModelName = "ailangaugemodelTXTCModel";
    private static final String nerBucketName = "<Specify name of your training data bucket here for NER>";
    private static final String txtcBucketName = "<Specify name of your training data bucket here for TXTC>";
    private static final String namespace_name = "<Specify the namespace here>";
    private static final String nerObjectName = "<Specify training file name here for NER>";
    private static final String txtcObjectName = "<Specify training file name here for TXTC>";
    private static String projectId;
    private static String nerModelId;
    private static String txtcModelId;
    private static String nerEndpointId;
    private static String txtcEndpointId;
    private static final String entext = "The Indy Autonomous Challenge is the worlds first head-to-head, high speed autonomous race taking place at the Indianapolis Motor Speedway";
    private static final String spanishText = "Este es un texto en el idioma de mi madre, la mejor mamá del mundo.";

    private static AIServiceLanguageClient client;

    public static void main(String[] args) {
        try {
            /* Step 1: Just reading a config file with my credentials so the application acts on my behalf */
            final ConfigFileReader.ConfigFile configFile =
                    ConfigFileReader.parse("<PATH TO YOUR CONFIG FILE>", "DEFAULT");

            final AuthenticationDetailsProvider provider =
                    new ConfigFileAuthenticationDetailsProvider(configFile);

            /* Step 2: Create a service client */
            client = AIServiceLanguageClient.builder().build(provider);

            /* Custom Models */
            /* Create an object */
            CustomModelsSample aiServiceLanguageExample = new CustomModelsSample();

            // Create AiLanguageProject
            Project languageProject = aiServiceLanguageExample.createLanguageProject();
            projectId = languageProject.getId();
            System.out.println(languageProject.toString());

            // wait till project state becomes ACTIVE
            while (languageProject.getLifecycleState() == Project.LifecycleState.Creating){
                System.out.println("Waiting for project creation to complete...");
                Thread.sleep(4000);
                languageProject = aiServiceLanguageExample.getLanguageProject(projectId);
            }
            languageProject = aiServiceLanguageExample.getLanguageProject(projectId);
            System.out.println("Project status changed to " + languageProject.getLifecycleState());

            /* Create and train Custom NER Model */
            // Create and train Custom NER AilanguageModel
            Model nerLanguageModel = aiServiceLanguageExample.createNERLanguageModel(nerModelName, nerBucketName, nerObjectName);
            nerModelId =  nerLanguageModel.getId();
            System.out.println(nerLanguageModel.toString());

            // wait till model state becomes ACTIVE
            while (nerLanguageModel.getLifecycleState() == Model.LifecycleState.Creating){
                System.out.println("Waiting for model training to complete...");
                Thread.sleep(60000);
                nerLanguageModel = aiServiceLanguageExample.getLanguageModel(nerModelId);
            }
            nerLanguageModel = aiServiceLanguageExample.getLanguageModel(nerModelId);
            System.out.println("Model status changed to " + nerLanguageModel.getLifecycleState());

            System.out.println("Printing model evaluation results");
            System.out.println(nerLanguageModel.getEvaluationResults());

            // Create AiLanguageEndpoint
            Endpoint nerLanguageEndpoint = aiServiceLanguageExample.createLanguageEndpoint(nerModelId);
            nerEndpointId = nerLanguageEndpoint.getId();
            System.out.println(nerLanguageEndpoint.toString());

            // wait till endpoint state becomes ACTIVE
            while (nerLanguageEndpoint.getLifecycleState() == Endpoint.LifecycleState.Creating){
                System.out.println("Waiting for endpoint creation to complete...");
                Thread.sleep(60000);
                nerLanguageEndpoint = aiServiceLanguageExample.getLanguageEndpoint(nerEndpointId);
            }
            nerLanguageEndpoint = aiServiceLanguageExample.getLanguageEndpoint(nerEndpointId);
            System.out.println("Endpoint status changed to " + nerLanguageEndpoint.getLifecycleState());

            // Inferencing on Custom Named Entity recognition model
            String customDetectLanguageEntitiesResponse = aiServiceLanguageExample.getBatchDetectLanguageEntities(entext);
            System.out.println(customDetectLanguageEntitiesResponse.toString());

            /* Create and train Custom Text classification Model */

            // Create and train Custom Text classification AilanguageModel
            Model txtcLanguageModel = aiServiceLanguageExample.createTXTCLanguageModel(txtcModelName, txtcBucketName, txtcObjectName);
            txtcModelId =  txtcLanguageModel.getId();
            System.out.println(txtcLanguageModel.toString());

            // wait till model state becomes ACTIVE
            while (txtcLanguageModel.getLifecycleState() == Model.LifecycleState.Creating){
                System.out.println("Waiting for model training to complete...");
                Thread.sleep(60000);
                txtcLanguageModel = aiServiceLanguageExample.getLanguageModel(txtcModelId);
            }
            txtcLanguageModel = aiServiceLanguageExample.getLanguageModel(txtcModelId);
            System.out.println("Model status changed to " + txtcLanguageModel.getLifecycleState());


            // Create AiLanguageEndpoint
            Endpoint txtcLanguageEndpoint = aiServiceLanguageExample.createLanguageEndpoint(txtcModelId);
            txtcEndpointId = txtcLanguageEndpoint.getId();
            System.out.println(txtcLanguageEndpoint.toString());

            // wait till endpoint state becomes ACTIVE
            while (txtcLanguageEndpoint.getLifecycleState() == Endpoint.LifecycleState.Creating){
                System.out.println("Waiting for endpoint creation to complete...");
                Thread.sleep(60000);
                txtcLanguageEndpoint = aiServiceLanguageExample.getLanguageEndpoint(txtcEndpointId);
            }
            txtcLanguageEndpoint = aiServiceLanguageExample.getLanguageEndpoint(txtcEndpointId);
            System.out.println("Endpoint status changed to " + txtcLanguageEndpoint.getLifecycleState());

            // Inferencing on Custom Text classification model
            String customDetectLanguageTextClassificationResponse = aiServiceLanguageExample.getBatchDetectLanguageTextClassification(entext);
            System.out.println(customDetectLanguageTextClassificationResponse.toString());

            client.close();
        } catch(InterruptedException | IOException e) {
            e.printStackTrace();
        }
    }

    // Create AiLanguageProject
    private Project createLanguageProject() {
        CreateProjectDetails projectDetails = CreateProjectDetails.builder().compartmentId(compartmentId).build();
        CreateProjectRequest request = CreateProjectRequest.builder().createProjectDetails(projectDetails).build();
        CreateProjectResponse response = client.createProject(request);
        return response.getProject();
    }

    // Get AiLanguageProject
    private Project getLanguageProject(String projectOcid) {
        GetProjectRequest request = GetProjectRequest.builder().projectId(projectOcid).build();
        GetProjectResponse response = client.getProject(request);
        return response.getProject();
    }

    // Create NER AiLanguageModel
    private Model createNERLanguageModel(String modelName, String bucketName, String objectName) {
        ModelDetails modeldtls = NamedEntityRecognitionModelDetails.builder().languageCode("en").build();
        java.util.List<String> trainingDataobjects = Arrays.asList(objectName);
        LocationDetails locationDetails = ObjectListDataset.builder().bucketName(bucketName).namespaceName(namespace_name).objectNames(trainingDataobjects).build();
        DatasetDetails trainingDataset = ObjectStorageDataset.builder().locationDetails(locationDetails).build();

        CreateModelDetails modelDetails = CreateModelDetails.builder()
                .compartmentId(compartmentId).displayName(modelName).projectId(projectId)
                .modelDetails(modeldtls).trainingDataset(trainingDataset).build();
        CreateModelRequest request = CreateModelRequest.builder().createModelDetails(modelDetails).build();
        CreateModelResponse response = client.createModel(request);
        return response.getModel();
    }

    // Create TXTC AiLanguageModel
    private Model createTXTCLanguageModel(String modelName, String bucketName, String objectName) {
        ModelDetails modeldtls = TextClassificationModelDetails.builder().languageCode("en").build();
        java.util.List<String> trainingDataobjects = Arrays.asList(objectName);
        LocationDetails locationDetails = ObjectListDataset.builder().bucketName(bucketName).namespaceName(namespace_name).objectNames(trainingDataobjects).build();
        DatasetDetails trainingDataset = ObjectStorageDataset.builder().locationDetails(locationDetails).build();

        CreateModelDetails modelDetails = CreateModelDetails.builder()
                .compartmentId(compartmentId).displayName(modelName).projectId(projectId)
                .modelDetails(modeldtls).trainingDataset(trainingDataset).build();
        CreateModelRequest request = CreateModelRequest.builder().createModelDetails(modelDetails).build();
        CreateModelResponse response = client.createModel(request);
        return response.getModel();
    }

    // Get AiLanguageModel
    private Model getLanguageModel(String modelOcid) {
        GetModelRequest request = GetModelRequest.builder().modelId(modelOcid).build();
        GetModelResponse response = client.getModel(request);
        return response.getModel();
    }

    // Create AiLanguageEndpoint
    private Endpoint createLanguageEndpoint(String modelId) {
        CreateEndpointDetails endpointDetails = CreateEndpointDetails.builder().compartmentId(compartmentId).modelId(modelId).inferenceUnits(1).build();
        CreateEndpointRequest request = CreateEndpointRequest.builder().createEndpointDetails(endpointDetails).build();
        CreateEndpointResponse response = client.createEndpoint(request);
        return response.getEndpoint();
    }

    // Get AiLanguageEndpoint
    private Endpoint getLanguageEndpoint(String endpointOcid) {
        GetEndpointRequest request = GetEndpointRequest.builder().endpointId(endpointOcid).build();
        GetEndpointResponse response = client.getEndpoint(request);
        return response.getEndpoint();
    }

    // Custom Named Entity Recognition
    private String getBatchDetectLanguageEntities(String text) {
        TextDocument textDocument = TextDocument.builder().text(text).languageCode("en").key("key1").build();
        java.util.List<TextDocument> documents = Arrays.asList(textDocument);
        BatchDetectLanguageEntitiesDetails details = BatchDetectLanguageEntitiesDetails.builder().endpointId(nerEndpointId).documents(documents).build();
        BatchDetectLanguageEntitiesRequest request = BatchDetectLanguageEntitiesRequest.builder().batchDetectLanguageEntitiesDetails(details).build();
        BatchDetectLanguageEntitiesResponse response = client.batchDetectLanguageEntities(request);
        return response.toString();
    }

    // Custom Text Classification
    private String getBatchDetectLanguageTextClassification(String text) {
        TextDocument textDocument = TextDocument.builder().text(text).languageCode("en").key("key1").build();
        java.util.List<TextDocument> documents = Arrays.asList(textDocument);
        BatchDetectLanguageTextClassificationDetails details = BatchDetectLanguageTextClassificationDetails.builder().endpointId(txtcEndpointId).documents(documents).build();
        BatchDetectLanguageTextClassificationRequest request = BatchDetectLanguageTextClassificationRequest.builder().batchDetectLanguageTextClassificationDetails(details).build();
        BatchDetectLanguageTextClassificationResponse response = client.batchDetectLanguageTextClassification(request);
        return response.toString();
    }
}
