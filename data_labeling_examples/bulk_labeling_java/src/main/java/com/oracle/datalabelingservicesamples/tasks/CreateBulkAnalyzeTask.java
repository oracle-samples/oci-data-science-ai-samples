package com.oracle.datalabelingservicesamples.tasks;


import com.oracle.bmc.datalabelingservicedataplane.model.CreateAnnotationDetails;
import com.oracle.bmc.datalabelingservicedataplane.model.RecordSummary;
import com.oracle.datalabelingservicesamples.labelingstrategies.MlAssistedLabelingStrategy;
import com.oracle.datalabelingservicesamples.requests.AssistedLabelingParams;
import com.oracle.pic.commons.exceptions.server.RenderableException;
import javassist.tools.reflect.CannotCreateException;
import lombok.extern.slf4j.Slf4j;

import java.security.InvalidParameterException;
import java.util.List;
import java.util.NoSuchElementException;

@Slf4j
public class CreateBulkAnalyzeTask extends Tasks<List<CreateAnnotationDetails>> {
    private final MlAssistedLabelingStrategy mlAssistedLabelingStrategy;
    private final List<RecordSummary> recordSummaries;

    private final AssistedLabelingParams assistedLabelingParams;

    public CreateBulkAnalyzeTask(
            MlAssistedLabelingStrategy mlAssistedLabelingStrategy,
            List<RecordSummary> recordSummaries,
            AssistedLabelingParams assistedLabelingParams) {
        this.mlAssistedLabelingStrategy = mlAssistedLabelingStrategy;
        this.recordSummaries = recordSummaries;
        this.assistedLabelingParams = assistedLabelingParams;
    }

    @Override
    public List<CreateAnnotationDetails> call() {
        List<CreateAnnotationDetails> createAnnotationDetails = null;
        try {
            createAnnotationDetails =
                    mlAssistedLabelingStrategy.bulkAnalyzeRecords(
                            recordSummaries, assistedLabelingParams);
        } catch (Exception e) {
            log.error("Error is {}", e.getMessage());
        }
        return createAnnotationDetails;
    }
}
