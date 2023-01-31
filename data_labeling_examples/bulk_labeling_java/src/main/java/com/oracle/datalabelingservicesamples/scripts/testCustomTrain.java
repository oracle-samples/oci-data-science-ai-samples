package com.oracle.datalabelingservicesamples.scripts;

import com.oracle.bmc.ailanguage.model.CreateEndpointDetails;
import com.oracle.bmc.ailanguage.model.OperationStatus;
import com.oracle.bmc.ailanguage.model.WorkRequest;
import com.oracle.bmc.ailanguage.requests.CreateEndpointRequest;
import com.oracle.bmc.ailanguage.requests.GetEndpointRequest;
import com.oracle.bmc.ailanguage.responses.CreateEndpointResponse;
import com.oracle.bmc.ailanguage.responses.GetEndpointResponse;
import com.oracle.bmc.aivision.requests.GetModelRequest;
import com.oracle.bmc.aivision.requests.GetProjectRequest;
import com.oracle.bmc.aivision.responses.GetModelResponse;
import com.oracle.bmc.aivision.responses.GetProjectResponse;
import com.oracle.datalabelingservicesamples.requests.Config;
import lombok.extern.slf4j.Slf4j;

import java.util.UUID;

@Slf4j
public class testCustomTrain {
    public static void main(String[] args) {
        final String visionModelId = "ocid1.aivisionmodel.oc1.phx.amaaaaaaniob46iazrkx6ir57egwpbcmfstr6lgwxzle4tw7qkkkoilmuita";
        final String visionProjectId = "ocid1.aivisionproject.oc1.phx.amaaaaaaniob46iaf4m7a2kgs7ysguaycarzmewo4ksu45wwwapv6n5h47kq";
        final String languageModelId = "";
        final String languageProjectId = "ocid1.ailanguageproject.oc1.phx.amaaaaaaniob46ialk4auijqqk4jtomix2ktqu2bngy5rl5xxqsu6rfloa7q";

//        Test access to existing projects

//        GetProjectRequest getProjectRequest =
//                GetProjectRequest.builder()
//                        .projectId(visionProjectId)
//                        .build();
//
//        GetModelRequest getVisionModelRequest =
//                GetModelRequest.builder()
//                        .modelId(visionModelId)
//                        .build();
//
//        GetProjectResponse getVisionProjectResponse = Config.INSTANCE.getAiVisionClient().getProject(getProjectRequest);
//        GetModelResponse getVisionModelResponse = Config.INSTANCE.getAiVisionClient().getModel(getVisionModelRequest);
//
//        log.info("Vision project :{}", getVisionProjectResponse.getProject().toString());
//        log.info("Vision Model :{}", getVisionModelResponse.getModel().toString());

        com.oracle.bmc.ailanguage.requests.GetProjectRequest getLanguageProjectRequest =
                com.oracle.bmc.ailanguage.requests.GetProjectRequest.builder()
                        .projectId(languageProjectId)
                        .build();

        com.oracle.bmc.ailanguage.requests.GetModelRequest getLanguageModelRequest =
                com.oracle.bmc.ailanguage.requests.GetModelRequest.builder()
                        .modelId(languageModelId)
                        .build();

//        com.oracle.bmc.ailanguage.responses.GetProjectResponse getLanguageProjectResponse = Config.INSTANCE.getAiLanguageClient().getProject(getLanguageProjectRequest);
//        com.oracle.bmc.ailanguage.responses.GetModelResponse getLanguageModelResponse = Config.INSTANCE.getAiLanguageClient().getModel(getLanguageModelRequest);
//
//        log.info("Language project :{}", getLanguageProjectResponse.getProject().toString());
//        log.info("Language Model :{}", getLanguageModelResponse.getModel().toString());

        /* Create endpoint mapping to given model id */
        CreateEndpointDetails createEndpointDetails = CreateEndpointDetails.builder()
                .displayName("EndPoint" + "-" + UUID.randomUUID().toString())
                .compartmentId("ocid1.compartment.oc1..aaaaaaaac76csgouljnw4gyxicjsoaq5uqoztxl6dkdqbwwokuysc7ssv6uq")
                .modelId("ocid1.ailanguagemodel.oc1.phx.amaaaaaaniob46iamuvfe7quqc3tmshrfrt2ddquj5b4rhgepel6mrmqbeaq")
                .inferenceUnits(1)
                .build();

        CreateEndpointRequest createEndpointRequest =
                CreateEndpointRequest.builder()
                        .createEndpointDetails(createEndpointDetails)
                        .build();

        CreateEndpointResponse createEndpointResponse = Config.INSTANCE.getAiLanguageClient().createEndpoint(createEndpointRequest);

        log.info("Created EndPoint  Response :{}", createEndpointResponse);
        log.info("Created EndPoint ID  :{}", createEndpointResponse.getEndpoint().getId());
        log.info("Display name  EndPoint  :{}", createEndpointResponse.getEndpoint().getDisplayName());
//
//    GetEndpointRequest request = GetEndpointRequest.builder().endpointId("ocid1.ailanguageendpoint.oc1.phx.amaaaaaaniob46iakynza3bqfcar3wnreeg4miwoqpnioxqlc2cbbr2ymiaa").build();
//        GetEndpointResponse response = Config.INSTANCE.getAiLanguageClient().getEndpoint(request);
//        log.info("Endpoint metadata :{} ", response.getEndpoint());

//    com.oracle.bmc.ailanguage.responses.GetModelResponse getLanguageModelResponse = Config.INSTANCE.getAiLanguageClient().getModel(getLanguageModelRequest);

//    log.info("Model from language :{}", getLanguageModelResponse.getModel().toString());
    }
}
