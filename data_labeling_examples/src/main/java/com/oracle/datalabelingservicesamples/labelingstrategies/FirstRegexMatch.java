package com.oracle.datalabelingservicesamples.labelingstrategies;

import java.util.Arrays;
import java.util.List;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import com.oracle.bmc.datalabelingservicedataplane.model.RecordSummary;
import com.oracle.datalabelingservicesamples.requests.Config;

public class FirstRegexMatch implements LabelingStrategy {

	private static final Pattern pattern = Pattern.compile(Config.INSTANCE.getRegexPattern());

	@Override
	public List<String> getLabel(RecordSummary record) {
		Matcher m = pattern.matcher(record.getName());
		if (m.find()) {
			String firstGroup = m.group(0);
			for (String label : Config.INSTANCE.getLabels()) {
				if (label.equals(firstGroup)) {
					return Arrays.asList(label);
				}
			}
		}
		return null;
	}
}
