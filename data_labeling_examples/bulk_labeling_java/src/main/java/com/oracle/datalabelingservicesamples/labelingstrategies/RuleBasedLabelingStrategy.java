package com.oracle.datalabelingservicesamples.labelingstrategies;

import java.util.List;

import com.oracle.bmc.datalabelingservicedataplane.model.RecordSummary;

public interface RuleBasedLabelingStrategy {

	public List<String> getLabel(RecordSummary record);
}
