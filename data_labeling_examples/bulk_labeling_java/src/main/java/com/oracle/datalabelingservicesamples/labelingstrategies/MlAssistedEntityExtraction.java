package com.oracle.datalabelingservicesamples.labelingstrategies;

import com.oracle.bmc.ailanguage.model.BatchDetectLanguageEntitiesDetails;
import com.oracle.bmc.ailanguage.model.EntityDocument;
import com.oracle.bmc.ailanguage.model.EntityDocumentResult;
import com.oracle.bmc.ailanguage.model.HierarchicalEntity;
import com.oracle.bmc.ailanguage.requests.BatchDetectLanguageEntitiesRequest;
import com.oracle.bmc.ailanguage.responses.BatchDetectLanguageEntitiesResponse;
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
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.io.IOUtils;

import java.io.IOException;
import java.math.BigDecimal;
import java.util.ArrayList;
import java.util.List;

@Slf4j
public class MlAssistedEntityExtraction implements AssistedLabelingStrategy {

    @Override
    public List<CreateAnnotationDetails> bulkAnalyzeRecords(List<RecordSummary> recordSummaries, AssistedLabelingParams assistedLabelingParams) {
        List<EntityDocument> documentList = new ArrayList<>();
        for (RecordSummary recordSummary : recordSummaries) {
            GetRecordContentRequest recordContentRequest =
                    GetRecordContentRequest.builder().recordId(recordSummary.getId()).build();
            GetRecordContentResponse recordContentResponse =
                    Config.INSTANCE.getDlsDpClient().getRecordContent(recordContentRequest);
            String documentText = "";
            try {
                documentText = IOUtils.toString(recordContentResponse.getInputStream(), "UTF-8");
                log.info("record content info : {}", documentText);
            } catch (IOException e) {
                e.printStackTrace();
            }
            documentList.add(
                    EntityDocument.builder()
                            .key(recordSummary.getId())
                            .text(documentText)
                            .build());
        }
        BatchDetectLanguageEntitiesDetails languageEntitiesDetails =
                BatchDetectLanguageEntitiesDetails.builder().documents(documentList).build();

        BatchDetectLanguageEntitiesRequest languageEntitiesRequest =
                BatchDetectLanguageEntitiesRequest.builder()
                        .batchDetectLanguageEntitiesDetails(languageEntitiesDetails)
                        .build();
        try {
            /* Send request to the Client */
            BatchDetectLanguageEntitiesResponse languageEntitiesResponse =
                    Config.INSTANCE.getAiLanguageClient().batchDetectLanguageEntities(languageEntitiesRequest);
            log.info(
                    "Response of language entity detection : {} ",
                    languageEntitiesResponse.getBatchDetectLanguageEntitiesResult().getDocuments());

            List<CreateAnnotationDetails> createAnnotationDetails = new ArrayList<>();
            for (EntityDocumentResult document :
                    languageEntitiesResponse
                            .getBatchDetectLanguageEntitiesResult()
                            .getDocuments()) {
                List<Entity> entities =
                        mapToDLSEntities(
                                assistedLabelingParams.getDlsDatasetLabels(), document.getEntities(), assistedLabelingParams.getConfidenceThreshold());
                if (!entities.isEmpty()) {
                    // TODO - compartment ID
                    createAnnotationDetails.add(
                            new CreateAnnotationDetails(
                                    document.getKey(),
                                    "assistedLabelingParams.getCompartmentId()",
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
            log.info("label from language {}", entity.getType());
            if (dlsLabels.contains(entity.getType())
                    && entity.getScore() >= confidenceThreshold) {
                languageLabels.add(
                        Label.builder()
                                .label(entity.getType())
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

    @Override
    public List<String> getLabel(RecordSummary record) {
        return null;
    }
}
