package com.oracle.datalabelingservicesamples.tasks;


import com.oracle.bmc.datalabelingservicedataplane.model.CreateAnnotationDetails;
import com.oracle.bmc.datalabelingservicedataplane.model.RecordSummary;
import com.oracle.datalabelingservicesamples.labelingstrategies.AssistedLabelingStrategy;
import lombok.extern.slf4j.Slf4j;

import java.util.List;

@Slf4j
public class CreateBulkAnalyzeTask extends Tasks<List<CreateAnnotationDetails>> {
    private final AssistedLabelingStrategy assistedLabelingStrategy;
    private final List<RecordSummary> recordSummaries;

    private final List<String> dlsDatasetLabels;

    public CreateBulkAnalyzeTask(
            AssistedLabelingStrategy assistedLabelingStrategy,
            List<RecordSummary> recordSummaries,
            List<String> dlsDatasetLabels) {
        this.assistedLabelingStrategy = assistedLabelingStrategy;
        this.recordSummaries = recordSummaries;
        this.dlsDatasetLabels = dlsDatasetLabels;
    }

    @Override
    public List<CreateAnnotationDetails> call() throws Exception {
        List<CreateAnnotationDetails> createAnnotationDetails = null;
        try {
            createAnnotationDetails =
                    assistedLabelingStrategy.bulkAnalyzeRecords(
                            recordSummaries, dlsDatasetLabels);
        } catch (Exception e) {
            log.error("Error is {}", e.getMessage());
        }
        return createAnnotationDetails;
    }
}
