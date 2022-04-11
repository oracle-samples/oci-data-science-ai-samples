package com.oracle.datalabelingservicesamples.labelingstrategies;

import java.util.Arrays;
import java.util.List;

import com.oracle.bmc.datalabelingservicedataplane.model.RecordSummary;
import com.oracle.datalabelingservicesamples.requests.Config;

public class FirstLetterMatch implements LabelingStrategy {

	@Override
	public List<String> getLabel(RecordSummary record) {
		for (String label : Config.INSTANCE.getLabels()) {
			if (record.getName().startsWith(label)) {
				return Arrays.asList(label);
			}
		}
		return null;
	}
}
