package com.oracle.datalabelingservicesamples.tasks;

import com.oracle.bmc.datalabelingservicedataplane.model.CreateAnnotationDetails;
import com.oracle.bmc.datalabelingservicedataplane.model.RecordSummary;
import com.oracle.datalabelingservicesamples.labelingstrategies.AssistedLabelingStrategy;
import com.oracle.datalabelingservicesamples.requests.AssistedLabelingParams;
import com.oracle.datalabelingservicesamples.utils.DataPlaneAPIWrapper;

import java.util.List;

public class TaskProvider {
    public CreateAnnotationTask getCreateAnnotationTask(
            CreateAnnotationDetails createAnnotationDetails,
            DataPlaneAPIWrapper dataPlaneAPIWrapper,
            String opcRequestId) {
        return new CreateAnnotationTask(
                createAnnotationDetails, opcRequestId, dataPlaneAPIWrapper);
    }

    public CreateBulkAnalyzeTask provideAssistedLabellingTask(
            AssistedLabelingStrategy assistedLabelingStrategy,
            List<RecordSummary> recordSummaries,
            AssistedLabelingParams assistedLabelingParams) {
        return new CreateBulkAnalyzeTask(
                assistedLabelingStrategy,
                recordSummaries,
                assistedLabelingParams);
    }
}
