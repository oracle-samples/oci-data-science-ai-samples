package com.oracle.datalabelingservicesamples.tasks;


import com.oracle.bmc.datalabelingservicedataplane.model.CreateAnnotationDetails;
import com.oracle.bmc.datalabelingservicedataplane.model.RecordSummary;
import com.oracle.datalabelingservicesamples.labelingstrategies.AssistedLabelingStrategy;
import com.oracle.datalabelingservicesamples.requests.AssistedLabelingParams;
import lombok.extern.slf4j.Slf4j;

import java.util.List;

@Slf4j
public class CreateBulkAnalyzeTask extends Tasks<List<CreateAnnotationDetails>> {
    private final AssistedLabelingStrategy assistedLabelingStrategy;
    private final List<RecordSummary> recordSummaries;

    private final AssistedLabelingParams assistedLabelingParams;

    public CreateBulkAnalyzeTask(
            AssistedLabelingStrategy assistedLabelingStrategy,
            List<RecordSummary> recordSummaries,
            AssistedLabelingParams assistedLabelingParams) {
        this.assistedLabelingStrategy = assistedLabelingStrategy;
        this.recordSummaries = recordSummaries;
        this.assistedLabelingParams = assistedLabelingParams;
    }

    @Override
    public List<CreateAnnotationDetails> call() {
        List<CreateAnnotationDetails> createAnnotationDetails = null;
        try {
            createAnnotationDetails =
                    assistedLabelingStrategy.bulkAnalyzeRecords(
                            recordSummaries, assistedLabelingParams);
        } catch (Exception e) {
            log.error("Error is {}", e.getMessage());
        }
        return createAnnotationDetails;
    }
}
