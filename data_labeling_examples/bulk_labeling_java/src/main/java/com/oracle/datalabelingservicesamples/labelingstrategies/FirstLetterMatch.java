package com.oracle.datalabelingservicesamples.labelingstrategies;

import java.util.Arrays;
import java.util.List;

import com.oracle.bmc.datalabelingservicedataplane.model.RecordSummary;
import com.oracle.datalabelingservicesamples.requests.Config;

public class FirstLetterMatch implements RuleBasedLabelingStrategy {

	@Override
	public List<String> getLabel(RecordSummary record) {
		for (String label : Config.INSTANCE.getLabels()) {
			if (record.getName().startsWith(String.valueOf(label.charAt(0)))) {
				return Arrays.asList(label);
			}
		}
		return null;
	}
}
