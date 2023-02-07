package com.oracle.datalabelingservicesamples.labelingstrategies;

import com.oracle.bmc.datalabelingservicedataplane.model.CreateAnnotationDetails;
import com.oracle.bmc.datalabelingservicedataplane.model.RecordSummary;
import com.oracle.datalabelingservicesamples.requests.AssistedLabelingParams;

import java.util.List;

public interface MlAssistedLabelingStrategy {
	String OUTPUT_LOCATION_PREFIX = "AssitedLabellingOutput";
	public List<CreateAnnotationDetails> bulkAnalyzeRecords(List<RecordSummary> records, AssistedLabelingParams assistedLabelingParams) throws Exception;
}
