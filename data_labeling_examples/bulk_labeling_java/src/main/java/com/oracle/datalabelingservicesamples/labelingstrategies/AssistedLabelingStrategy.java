package com.oracle.datalabelingservicesamples.labelingstrategies;

import com.oracle.bmc.datalabelingservicedataplane.model.CreateAnnotationDetails;
import com.oracle.bmc.datalabelingservicedataplane.model.RecordSummary;

import java.util.List;

public interface AssistedLabelingStrategy extends LabelingStrategy{
	String OUTPUT_LOCATION_PREFIX = "AssitedLabellingOutput";
	public List<CreateAnnotationDetails> bulkAnalyzeRecords(List<RecordSummary> records, List<String> dlsLabels) throws Exception;
}
