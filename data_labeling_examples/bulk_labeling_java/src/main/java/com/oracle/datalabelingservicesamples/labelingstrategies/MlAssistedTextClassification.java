package com.oracle.datalabelingservicesamples.labelingstrategies;

import com.oracle.bmc.ailanguage.model.BatchDetectLanguageTextClassificationDetails;
import com.oracle.bmc.ailanguage.model.TextClassification;
import com.oracle.bmc.ailanguage.model.TextClassificationDocument;
import com.oracle.bmc.ailanguage.model.TextClassificationDocumentResult;
import com.oracle.bmc.ailanguage.requests.BatchDetectLanguageTextClassificationRequest;
import com.oracle.bmc.ailanguage.responses.BatchDetectLanguageTextClassificationResponse;
import com.oracle.bmc.datalabelingservicedataplane.model.CreateAnnotationDetails;
import com.oracle.bmc.datalabelingservicedataplane.model.Entity;
import com.oracle.bmc.datalabelingservicedataplane.model.GenericEntity;
import com.oracle.bmc.datalabelingservicedataplane.model.Label;
import com.oracle.bmc.datalabelingservicedataplane.model.RecordSummary;
import com.oracle.bmc.datalabelingservicedataplane.requests.GetRecordContentRequest;
import com.oracle.bmc.datalabelingservicedataplane.responses.GetRecordContentResponse;
import com.oracle.datalabelingservicesamples.constants.DataLabelingConstants;
import com.oracle.datalabelingservicesamples.requests.AssistedLabelingParams;
import com.oracle.datalabelingservicesamples.requests.Config;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.collections4.ListUtils;
import org.apache.commons.io.IOUtils;

import java.io.IOException;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

@Slf4j
public class MlAssistedTextClassification implements AssistedLabelingStrategy {

    @Override
    public List<CreateAnnotationDetails> bulkAnalyzeRecords(List<RecordSummary> recordSummaries, AssistedLabelingParams assistedLabelingParams) {
        List<TextClassificationDocument> documentList = new ArrayList<>();
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
                    TextClassificationDocument.builder()
                            .key(recordSummary.getId())
                            .text(documentText)
                            .build());
        }
        BatchDetectLanguageTextClassificationDetails textClassificationDetails =
                BatchDetectLanguageTextClassificationDetails.builder().documents(documentList).build();

        BatchDetectLanguageTextClassificationRequest textClassificationRequest =
                BatchDetectLanguageTextClassificationRequest.builder()
                        .batchDetectLanguageTextClassificationDetails(textClassificationDetails)
                        .build();
        try {
            /* Send request to the Client */
            BatchDetectLanguageTextClassificationResponse textClassificationResponse =
                    Config.INSTANCE.getAiLanguageClient().batchDetectLanguageTextClassification(textClassificationRequest);
            log.info(
                    "Response of language entity detection : {} ",
                    textClassificationResponse.getBatchDetectLanguageTextClassificationResult().getDocuments());

            List<CreateAnnotationDetails> createAnnotationDetails = new ArrayList<>();
            for (TextClassificationDocumentResult document :
                    textClassificationResponse
                            .getBatchDetectLanguageTextClassificationResult()
                            .getDocuments()) {
                List<Entity> entities =
                        mapToDLSEntities(
                                assistedLabelingParams.getDlsDatasetLabels(), document.getTextClassification(), assistedLabelingParams.getConfidenceThreshold());
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

    public List<Entity> mapToDLSEntities(List<String> dlsLabels, List<TextClassification> textClassifications, float confidenceThreshold) {
        List<Entity> entityList = new ArrayList<>();
        List<Label> languageLabels = new ArrayList<>();
        TextClassification textClassification;
        if(!textClassifications.isEmpty()) {
            textClassification = textClassifications.get(0);
            if (dlsLabels.contains(textClassification.getLabel())
                    && textClassification.getScore() >= confidenceThreshold) {
                languageLabels.add(
                        Label.builder()
                                .label(textClassification.getLabel())
                                .build());
                Entity genericEntity =
                        GenericEntity.builder()
                                .labels(languageLabels)
                                .build();
                entityList.add(genericEntity);
            }
        }
        return entityList;
    }

    @Override
    public List<String> getLabel(RecordSummary record) {
        return null;
    }
}
