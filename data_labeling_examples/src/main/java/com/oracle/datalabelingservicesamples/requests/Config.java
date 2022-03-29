package com.oracle.datalabelingservicesamples.requests;

import java.io.IOException;
import java.util.Arrays;
import java.util.List;
import java.util.Map;
import java.util.Properties;

import org.apache.commons.lang3.exception.ExceptionUtils;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.oracle.bmc.ConfigFileReader;
import com.oracle.bmc.auth.AuthenticationDetailsProvider;
import com.oracle.bmc.auth.ConfigFileAuthenticationDetailsProvider;
import com.oracle.bmc.datalabelingservicedataplane.DataLabelingClient;
import com.oracle.datalabelingservicesamples.labelingstrategies.CustomLabelMatch;
import com.oracle.datalabelingservicesamples.labelingstrategies.FirstLetterMatch;
import com.oracle.datalabelingservicesamples.labelingstrategies.FirstRegexMatch;
import com.oracle.datalabelingservicesamples.labelingstrategies.LabelingStrategy;

import lombok.Getter;
import lombok.extern.slf4j.Slf4j;

@Getter
@Slf4j
public enum Config {

	INSTANCE;

	private DataLabelingClient dlsDpClient;
	private String configFilePath;
	private String configProfile;
	private String dpEndpoint;
	private String datasetId;
	private String region;

	private List<String> labels;
	private Map<String, List<String>> customLabels;
	private String labelingAlgorithm;
	private LabelingStrategy labelingStrategy;
	private String regexPattern;
	private int threadCount;

	private Config() {
		try {
			Properties config = new Properties();
			config.load(getClass().getClassLoader().getResourceAsStream("config.properties"));
			configFilePath = config.getProperty("CONFIG_FILE_PATH");
			configProfile = config.getProperty("CONFIG_PROFILE");
			dpEndpoint = config.getProperty("DLS_DP_URL");
			datasetId = config.getProperty("DATASET_ID");
			region = config.getProperty("REGION");
			labelingAlgorithm = config.getProperty("LABELING_ALGORITHM");
			String threadConfig = config.getProperty("THREAD_COUNT");
			if (!threadConfig.isEmpty()) {
				threadCount = Integer.parseInt(threadConfig);
			} else {
				threadCount = 20;
			}
			performAssertionOninput();
			initializeLabelingStrategy();
			validateAndInitializeLabels(config);
			dpEndpoint = dpEndpoint.replace("${REGION}", region);
			dlsDpClient = initializeDpClient();
		} catch (IOException ex) {
			ExceptionUtils.wrapAndThrow(ex);
		}
	}

	@SuppressWarnings("unchecked")
	private void validateAndInitializeLabels(Properties config) {
		switch (labelingAlgorithm) {
		case "FIRST_LETTER_MATCH":
		case "FIRST_REGEX_MATCH":
			labels = Arrays.asList(config.getProperty("LABELS").split(","));
			assert null != labels && labels.isEmpty() == false : "Labels Cannot be empty";
			break;
		case "CUSTOM_LABELS_MATCH":
			try {
				ObjectMapper mapper = new ObjectMapper();
				customLabels = mapper.readValue(config.getProperty("CUSTOM_LABELS"), Map.class);
			} catch (JsonProcessingException e) {
				log.error("Invalid Custom Labels Provided as Input");
				ExceptionUtils.wrapAndThrow(e);
			}

		}
		if (labelingAlgorithm.equals("FIRST_REGEX_MATCH")) {
			regexPattern = config.getProperty("FIRST_MATCH_REGEX_PATTERN");
		}
	}

	private void initializeLabelingStrategy() {
		switch (labelingAlgorithm) {
		case "FIRST_LETTER_MATCH":
			labelingStrategy = new FirstLetterMatch();
			break;

		case "FIRST_REGEX_MATCH":
			labelingStrategy = new FirstRegexMatch();
			break;
			
		case "CUSTOM_LABELS_MATCH":
			labelingStrategy = new CustomLabelMatch();
			break;
		}
	}

	private DataLabelingClient initializeDpClient() {
		ConfigFileReader.ConfigFile configFile = null;
		try {
			configFile = ConfigFileReader.parse(configFilePath, configProfile);
		} catch (IOException ioe) {
			log.error("Configuration file not found", ioe);
			ExceptionUtils.wrapAndThrow(ioe);
		}
		final AuthenticationDetailsProvider configFileProvider = new ConfigFileAuthenticationDetailsProvider(
				configFile);
		dlsDpClient = new DataLabelingClient(configFileProvider);
		dlsDpClient.setRegion(region);
		dlsDpClient.setEndpoint(dpEndpoint);
		return dlsDpClient;
	}

	private void performAssertionOninput() {
		assert configFilePath != null : "Config filepath cannot be empty";
		assert configProfile != null : "Config Profile cannot be empty";
		assert dpEndpoint != null : "DLS DP URL cannot be empty";
		assert datasetId != null : "Dataset Id cannot be empty";
		assert region != null : "Region Cannot be empty";
		assert labelingAlgorithm != null : "Labeling Strategy cannot be empty";
		assert threadCount >= 1 : "Invalid Thread Count Passed";
	}

}
