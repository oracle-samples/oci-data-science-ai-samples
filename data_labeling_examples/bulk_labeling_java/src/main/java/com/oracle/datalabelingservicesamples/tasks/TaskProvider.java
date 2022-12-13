package com.oracle.datalabelingservicesamples.tasks;

import com.oracle.bmc.datalabelingservicedataplane.model.CreateAnnotationDetails;
import com.oracle.bmc.datalabelingservicedataplane.model.RecordSummary;
import com.oracle.datalabelingservicesamples.labelingstrategies.MlAssistedLabelingStrategy;
import com.oracle.datalabelingservicesamples.requests.AssistedLabelingParams;
import com.oracle.datalabelingservicesamples.utils.DlsApiWrapper;

import java.util.List;

public class TaskProvider {
    public CreateAnnotationTask getCreateAnnotationTask(
            CreateAnnotationDetails createAnnotationDetails,
            DlsApiWrapper dlsApiWrapper,
            String opcRequestId) {
        return new CreateAnnotationTask(
                createAnnotationDetails, opcRequestId, dlsApiWrapper);
    }

    public CreateBulkAnalyzeTask provideAssistedLabellingTask(
            MlAssistedLabelingStrategy mlAssistedLabelingStrategy,
            List<RecordSummary> recordSummaries,
            AssistedLabelingParams assistedLabelingParams) {
        return new CreateBulkAnalyzeTask(
                mlAssistedLabelingStrategy,
                recordSummaries,
                assistedLabelingParams);
    }
}
