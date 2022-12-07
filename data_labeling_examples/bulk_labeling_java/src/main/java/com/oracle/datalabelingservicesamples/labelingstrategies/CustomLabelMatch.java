package com.oracle.datalabelingservicesamples.labelingstrategies;

import java.util.List;
import java.util.Map;
import java.util.Set;

import com.oracle.bmc.datalabelingservicedataplane.model.RecordSummary;
import com.oracle.datalabelingservicesamples.requests.Config;

public class CustomLabelMatch implements RuleBasedLabelingStrategy {

	@Override
	public List<String> getLabel(RecordSummary record) {
		Map<String, List<String>> bulkLabelRequest =  Config.INSTANCE.getCustomLabels();

		Set<String> paths = bulkLabelRequest.keySet();
		for (String path : paths) {
			if (record.getName().startsWith(path)) {
				return bulkLabelRequest.get(path);
			}
		}
		return null;
	}
}
