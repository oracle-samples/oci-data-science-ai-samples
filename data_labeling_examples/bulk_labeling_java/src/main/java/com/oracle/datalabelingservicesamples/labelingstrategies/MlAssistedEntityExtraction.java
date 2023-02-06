package com.oracle.datalabelingservicesamples.labelingstrategies;

import com.oracle.bmc.ailanguage.model.BatchDetectLanguageEntitiesDetails;
import com.oracle.bmc.ailanguage.model.CreateEndpointDetails;
import com.oracle.bmc.ailanguage.model.Endpoint;
import com.oracle.bmc.ailanguage.model.EntityDocumentResult;
import com.oracle.bmc.ailanguage.model.HierarchicalEntity;
import com.oracle.bmc.ailanguage.model.OperationStatus;
import com.oracle.bmc.ailanguage.model.SortOrder;
import com.oracle.bmc.ailanguage.model.TextDocument;
import com.oracle.bmc.ailanguage.model.WorkRequest;
import com.oracle.bmc.ailanguage.requests.BatchDetectLanguageEntitiesRequest;
import com.oracle.bmc.ailanguage.requests.CreateEndpointRequest;
import com.oracle.bmc.ailanguage.requests.ListEndpointsRequest;
import com.oracle.bmc.ailanguage.responses.BatchDetectLanguageEntitiesResponse;
import com.oracle.bmc.ailanguage.responses.CreateEndpointResponse;
import com.oracle.bmc.ailanguage.responses.ListEndpointsResponse;
import com.oracle.bmc.datalabelingservicedataplane.model.CreateAnnotationDetails;
import com.oracle.bmc.datalabelingservicedataplane.model.Entity;
import com.oracle.bmc.datalabelingservicedataplane.model.Label;
import com.oracle.bmc.datalabelingservicedataplane.model.RecordSummary;
import com.oracle.bmc.datalabelingservicedataplane.model.TextSelectionEntity;
import com.oracle.bmc.datalabelingservicedataplane.model.TextSpan;
import com.oracle.bmc.datalabelingservicedataplane.requests.GetRecordContentRequest;
import com.oracle.bmc.datalabelingservicedataplane.responses.GetRecordContentResponse;
import com.oracle.datalabelingservicesamples.requests.AssistedLabelingParams;
import com.oracle.datalabelingservicesamples.requests.Config;
import com.oracle.datalabelingservicesamples.workRequests.LanguageWorkRequestPollService;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.collections4.CollectionUtils;
import org.apache.commons.io.IOUtils;

import java.io.IOException;
import java.math.BigDecimal;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

@Slf4j
public class MlAssistedEntityExtraction implements MlAssistedLabelingStrategy {
    LanguageWorkRequestPollService languageWorkRequestPollService = new LanguageWorkRequestPollService();

    @Override
    public List<CreateAnnotationDetails> bulkAnalyzeRecords(List<RecordSummary> recordSummaries, AssistedLabelingParams assistedLabelingParams) throws Exception {
        List<TextDocument> documentList = new ArrayList<>();
        for (RecordSummary recordSummary : recordSummaries) {
            GetRecordContentRequest recordContentRequest =
                    GetRecordContentRequest.builder().recordId(recordSummary.getId()).build();
            GetRecordContentResponse recordContentResponse =
                    Config.INSTANCE.getDlsDpClient().getRecordContent(recordContentRequest);
            String documentText = "";
            try {
                documentText = IOUtils.toString(recordContentResponse.getInputStream(), "UTF-8");
            } catch (IOException e) {
                e.printStackTrace();
            }
            documentList.add(
                    TextDocument.builder()
                            .key(recordSummary.getId())
                            .text(documentText)
                            .build());
        }

        if(assistedLabelingParams.getMlModelType().equals("CUSTOM")) {
            setCustomLanguageModelEndpoint(assistedLabelingParams);
        }

        BatchDetectLanguageEntitiesDetails languageEntitiesDetails =
                BatchDetectLanguageEntitiesDetails.builder()
                        .documents(documentList)
                        .endpointId(assistedLabelingParams.getCustomModelEndpoint())
                        .build();

        BatchDetectLanguageEntitiesRequest languageEntitiesRequest =
                BatchDetectLanguageEntitiesRequest.builder()
                        .batchDetectLanguageEntitiesDetails(languageEntitiesDetails)
                        .build();
        try {
            /* Send request to the Client */
            BatchDetectLanguageEntitiesResponse languageEntitiesResponse =
                    Config.INSTANCE.getAiLanguageClient().batchDetectLanguageEntities(languageEntitiesRequest);

            List<CreateAnnotationDetails> createAnnotationDetails = new ArrayList<>();
            for (EntityDocumentResult document :
                    languageEntitiesResponse
                            .getBatchDetectLanguageEntitiesResult()
                            .getDocuments()) {
                List<Entity> entities =
                        mapToDLSEntities(
                                assistedLabelingParams.getDlsDatasetLabels(), document.getEntities(), assistedLabelingParams.getConfidenceThreshold());
                if (!entities.isEmpty()) {
                    createAnnotationDetails.add(
                            new CreateAnnotationDetails(
                                    document.getKey(),
                                    assistedLabelingParams.getCompartmentId(),
                                    entities,
                                    null,
                                    null));
                }
            }
            return createAnnotationDetails;
        } catch (Exception ex) {
            log.error("Error in bulkAnalyse - {}", ex.getMessage());
            throw ex;
        }
    }

    public List<Entity> mapToDLSEntities(List<String> dlsLabels, List<HierarchicalEntity> entities, float confidenceThreshold) {
        List<Entity> entityList = new ArrayList<>();
        for (HierarchicalEntity entity : entities) {
            List<Label> languageLabels = new ArrayList<>();
            dlsLabels = Collections.unmodifiableList(dlsLabels);
            List<String> dlsLabelsLowercase = (List<String>) CollectionUtils.collect(dlsLabels,
                    String::toLowerCase);
            dlsLabelsLowercase = Collections.unmodifiableList(dlsLabelsLowercase);
            if (dlsLabelsLowercase.contains(entity.getType().toLowerCase())
                    && entity.getScore() >= confidenceThreshold) {
                int indexOfLabel = dlsLabelsLowercase.indexOf(entity.getType().toLowerCase());
                languageLabels.add(
                        Label.builder()
                                .label(dlsLabels.get(indexOfLabel))
                                .build());
                Entity textSelectionEntity =
                        TextSelectionEntity.builder()
                                .labels(languageLabels)
                                .textSpan(
                                        TextSpan.builder()
                                                .offset(BigDecimal.valueOf(entity.getOffset()))
                                                .length(BigDecimal.valueOf(entity.getLength()))
                                                .build())
                                .build();
                entityList.add(textSelectionEntity);
            }
        }
        return entityList;
    }

    public void setCustomLanguageModelEndpoint(AssistedLabelingParams assistedLabelingParams) throws Exception {

            ListEndpointsRequest listEndpointsRequest = ListEndpointsRequest.builder()
                    .compartmentId(assistedLabelingParams.getCompartmentId())
                    .modelId(assistedLabelingParams.getCustomModelId())
                    .lifecycleState(Endpoint.LifecycleState.Active)
                    .sortOrder(SortOrder.Asc)
                    .sortBy(ListEndpointsRequest.SortBy.TimeCreated)
                    .build();

            try{
                log.info("Fetching endpoints for model ID :{}", assistedLabelingParams.getCustomModelId());
                ListEndpointsResponse listEndpointsResponse = Config.INSTANCE.getAiLanguageClient()
                        .listEndpoints(listEndpointsRequest);
                if(listEndpointsResponse.getEndpointCollection() != null){
                    if(!listEndpointsResponse.getEndpointCollection().getItems().isEmpty()){
                        String customModelEndpoint = listEndpointsResponse.getEndpointCollection().getItems().get(0).getId();
                        assistedLabelingParams.setCustomModelEndpoint(customModelEndpoint);
                        log.info("Language model endpoint set to : {} ", assistedLabelingParams.getCustomModelEndpoint());
                        return;
                    }
                }
            } catch (Exception ex) {
                throw new Exception("Error in fetching endpoints for custom model Id provided");
            }

            CreateEndpointDetails createEndpointDetails = CreateEndpointDetails.builder()
                    .compartmentId(assistedLabelingParams.getCompartmentId())
                    .description("Endpoint for model Id : " + assistedLabelingParams.getCustomModelId())
                    .modelId(assistedLabelingParams.getCustomModelId())
                    .build();

            CreateEndpointRequest createEndpointRequest =
                    CreateEndpointRequest.builder()
                            .createEndpointDetails(createEndpointDetails)
                            .build();

            try {
                log.info("No existing endpoint, creating a new endpoint for model Id :{}", assistedLabelingParams.getCustomModelId());
                CreateEndpointResponse createEndpointResponse = Config.INSTANCE.getAiLanguageClient().createEndpoint(createEndpointRequest);

                WorkRequest languageWorkrequest = languageWorkRequestPollService.pollLanguageWorkRequestStatus(createEndpointResponse.getOpcWorkRequestId());

                if (!languageWorkrequest.getStatus().equals(OperationStatus.Succeeded)) {
                    throw new Exception("Language endpoint creation failed, cannot proceed with inference");
                }

                assistedLabelingParams.setCustomModelEndpoint(createEndpointResponse.getEndpoint().getId());
            } catch (Exception ex) {
                throw new Exception("Error in creating an endpoint for custom model Id provided");
            }
    }
}
