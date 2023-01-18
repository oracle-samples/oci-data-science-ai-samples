package com.oracle.datalabelingservicesamples.requests;

import java.io.IOException;
import java.io.InputStream;
import java.util.Arrays;
import java.util.List;
import java.util.Map;
import java.util.Properties;
import java.util.regex.Pattern;

import com.oracle.bmc.auth.AuthenticationDetailsProvider;
import com.oracle.bmc.auth.ConfigFileAuthenticationDetailsProvider;
import org.apache.commons.lang3.StringUtils;
import org.apache.commons.lang3.exception.ExceptionUtils;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.oracle.bmc.ConfigFileReader;
import com.oracle.bmc.datalabelingservicedataplane.DataLabelingClient;
import com.oracle.bmc.objectstorage.ObjectStorageClient;
import com.oracle.datalabelingservicesamples.constants.DataLabelingConstants;
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
	private ObjectStorageClient objectStorageClient;

	private String configFilePath;
	private String configProfile;
	private int threadCount;

	private String dpEndpoint;
	private String objectStorageEndpoint;

	private String datasetId;
	private List<String> labels;
	private Map<String, List<String>> customLabels;
	private String labelingAlgorithm;
	private LabelingStrategy labelingStrategy;
	private String regexPattern;
	private Pattern pattern;

	private String objectStorageNameSpace;
	private String objectStorageBucket;
	private String datasetDirectory;

	private Config() {
		try {
			Properties config = new Properties();
			config.load(getClass().getClassLoader().getResourceAsStream("config.properties"));
			configFilePath = StringUtils.isEmpty(System.getProperty(DataLabelingConstants.CONFIG_FILE_PATH))
					? config.getProperty(DataLabelingConstants.CONFIG_FILE_PATH)
					: System.getProperty(DataLabelingConstants.CONFIG_FILE_PATH);
			configProfile = StringUtils.isEmpty(System.getProperty(DataLabelingConstants.CONFIG_PROFILE))
					? config.getProperty(DataLabelingConstants.CONFIG_PROFILE)
					: System.getProperty(DataLabelingConstants.CONFIG_PROFILE);
			dpEndpoint = StringUtils.isEmpty(System.getProperty(DataLabelingConstants.DLS_DP_URL))
					? config.getProperty(DataLabelingConstants.DLS_DP_URL)
					: System.getProperty(DataLabelingConstants.DLS_DP_URL);
			objectStorageEndpoint = StringUtils.isEmpty(System.getProperty(DataLabelingConstants.OBJECT_STORAGE_URL))
					? config.getProperty(DataLabelingConstants.OBJECT_STORAGE_URL)
					: System.getProperty(DataLabelingConstants.OBJECT_STORAGE_URL);
			datasetId = StringUtils.isEmpty(System.getProperty(DataLabelingConstants.DATASET_ID))
					? config.getProperty(DataLabelingConstants.DATASET_ID)
					: System.getProperty(DataLabelingConstants.DATASET_ID);
			labelingAlgorithm = StringUtils.isEmpty(System.getProperty(DataLabelingConstants.LABELING_ALGORITHM))
					? config.getProperty(DataLabelingConstants.LABELING_ALGORITHM)
					: System.getProperty(DataLabelingConstants.LABELING_ALGORITHM);
			objectStorageNameSpace = StringUtils.isEmpty(System.getProperty(DataLabelingConstants.OBJECT_STORAGE_NAMESPACE))
					? config.getProperty(DataLabelingConstants.OBJECT_STORAGE_NAMESPACE)
					: System.getProperty(DataLabelingConstants.OBJECT_STORAGE_NAMESPACE);
			objectStorageBucket = StringUtils.isEmpty(System.getProperty(DataLabelingConstants.OBJECT_STORAGE_BUCKET_NAME))
					? config.getProperty(DataLabelingConstants.OBJECT_STORAGE_BUCKET_NAME)
					: System.getProperty(DataLabelingConstants.OBJECT_STORAGE_BUCKET_NAME);
			datasetDirectory = StringUtils.isEmpty(System.getProperty(DataLabelingConstants.DATASET_DIRECTORY_PATH))
					? config.getProperty(DataLabelingConstants.DATASET_DIRECTORY_PATH)
					: System.getProperty(DataLabelingConstants.DATASET_DIRECTORY_PATH);
			String threadConfig = StringUtils.isEmpty(System.getProperty(DataLabelingConstants.THREAD_COUNT))
					? config.getProperty(DataLabelingConstants.THREAD_COUNT)
					: System.getProperty(DataLabelingConstants.THREAD_COUNT);
			threadCount = (!threadConfig.isEmpty()) ? Integer.parseInt(threadConfig)
					: DataLabelingConstants.DEFAULT_THREAD_COUNT;
			performAssertionOninput();
			validateAndInitialize(config);
		} catch (IOException ex) {
			ExceptionUtils.wrapAndThrow(ex);
		}
	}

	private void validateAndInitialize(Properties config) {
		switch (System.getProperty(DataLabelingConstants.TENANT))
		{
			case DataLabelingConstants.DLS:
				performAssertionOnDLSInput();
				initializeLabelingStrategy();
				validateAndInitializeLabels(config);
				initializeDpClient();
				break;
			case DataLabelingConstants.OBJECT_STORAGE:
				performAssertionOnObjectStorageInput();
				initializeObjectStorageClient();
		}
	}

	private void performAssertionOnObjectStorageInput() {
		assert objectStorageEndpoint != null : "OBJECT STORAGE URL cannot be empty";
		assert objectStorageBucket != null : "OBJECT STORAGE BUCKET NAME cannot be empty";
		assert objectStorageNameSpace != null : "OBJECT STORAGE NAMESPACE cannot be empty";
		assert datasetDirectory != null : "DATASET DIRECTORY PATH cannot be empty";
	}

	private void performAssertionOnDLSInput() {
		assert dpEndpoint != null : "DLS DP URL cannot be empty";
		assert datasetId != null : "Dataset Id cannot be empty";
		assert labelingAlgorithm != null : "Labeling Strategy cannot be empty";
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

	@SuppressWarnings("unchecked")
	private void validateAndInitializeLabels(Properties config) {
		switch (labelingAlgorithm) {
		case "FIRST_LETTER_MATCH":
		case "FIRST_REGEX_MATCH":
			String inputlLabels = StringUtils.isEmpty(System.getProperty(DataLabelingConstants.LABELS))
					? config.getProperty(DataLabelingConstants.LABELS)
					: System.getProperty(DataLabelingConstants.LABELS);
			labels = Arrays.asList(inputlLabels.split(","));
			assert null != labels && labels.isEmpty() == false : "Labels Cannot be empty";
			break;

		case "CUSTOM_LABELS_MATCH":
			try {
				String customLabel = StringUtils.isEmpty(System.getProperty(DataLabelingConstants.CUSTOM_LABELS))
						? config.getProperty(DataLabelingConstants.CUSTOM_LABELS)
						: System.getProperty(DataLabelingConstants.CUSTOM_LABELS);
				ObjectMapper mapper = new ObjectMapper();
				customLabels = mapper.readValue(customLabel, Map.class);
			} catch (JsonProcessingException e) {
				log.error("Invalid Custom Labels Provided as Input");
				ExceptionUtils.wrapAndThrow(e);
			}
			break;
		}

		if (labelingAlgorithm.equals("FIRST_REGEX_MATCH")) {
			regexPattern = StringUtils.isEmpty(System.getProperty(DataLabelingConstants.FIRST_MATCH_REGEX_PATTERN))
					? config.getProperty(DataLabelingConstants.FIRST_MATCH_REGEX_PATTERN)
					: System.getProperty(DataLabelingConstants.FIRST_MATCH_REGEX_PATTERN);
			pattern = Pattern.compile(regexPattern);
		}
	}

	private AuthenticationDetailsProvider getConfigFileProvider() {
		ConfigFileReader.ConfigFile configFile = null;
		try {
			configFile = ConfigFileReader.parse(configFilePath, configProfile);
		} catch (IOException ioe) {
			log.error("Configuration file not found", ioe);
			ExceptionUtils.wrapAndThrow(ioe);
		}
		final AuthenticationDetailsProvider configFileProvider = new ConfigFileAuthenticationDetailsProvider(
				configFile);

		return configFileProvider;
	}

	private void initializeObjectStorageClient() {
		objectStorageClient = new ObjectStorageClient(getProvider());
		objectStorageClient.setEndpoint(objectStorageEndpoint);
	}

	private void initializeDpClient() {
		dlsDpClient = new DataLabelingClient(getConfigFileProvider());
		dlsDpClient.setEndpoint(dpEndpoint);
	}

	private void performAssertionOninput() {
		assert configFilePath != null : "Config filepath cannot be empty";
		assert configProfile != null : "Config Profile cannot be empty";
		assert threadCount >= 1 : "Invalid Thread Count Passed";
	}

}

