package com.oracle.datalabelingservicesamples.requests;

import java.io.IOException;
import java.util.Arrays;
import java.util.List;
import java.util.Map;
import java.util.Properties;
import java.util.regex.Pattern;

import com.oracle.bmc.ailanguage.AIServiceLanguageClient;
import com.oracle.bmc.aivision.AIServiceVisionClient;
import com.oracle.bmc.objectstorage.ObjectStorageClient;
import com.oracle.datalabelingservicesamples.labelingstrategies.MlAssistedEntityExtraction;
import com.oracle.datalabelingservicesamples.labelingstrategies.MlAssistedImageClassification;
import com.oracle.datalabelingservicesamples.labelingstrategies.MlAssistedObjectDetection;
import com.oracle.datalabelingservicesamples.labelingstrategies.MlAssistedTextClassification;
import org.apache.commons.lang3.StringUtils;
import org.apache.commons.lang3.exception.ExceptionUtils;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.oracle.bmc.ConfigFileReader;
import com.oracle.bmc.auth.AuthenticationDetailsProvider;
import com.oracle.bmc.auth.ConfigFileAuthenticationDetailsProvider;
import com.oracle.bmc.datalabelingservicedataplane.DataLabelingClient;
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
	private AIServiceVisionClient aiVisionClient;
	private AIServiceLanguageClient aiLanguageClient;
	private ObjectStorageClient objectStorageClient;
	private String configFilePath;
	private String configProfile;
	private String dpEndpoint;
	private String region;
	private String datasetId;
	private String customModelId;
	private String mlModelType;

	private List<String> labels;
	private Map<String, List<String>> customLabels;
	private String labelingAlgorithm;
	private LabelingStrategy labelingStrategy;
	private AssistedLabelingParams assistedLabelingParams;
	private String regexPattern;
	private Pattern pattern;
	private int threadCount;

	private Config() {
		try {
			Properties config = new Properties();
			config.load(getClass().getClassLoader().getResourceAsStream("config.properties"));

			// TODO  get assisted labeling params
			configFilePath = StringUtils.isEmpty(System.getProperty(DataLabelingConstants.CONFIG_FILE_PATH))
					? config.getProperty(DataLabelingConstants.CONFIG_FILE_PATH)
					: System.getProperty(DataLabelingConstants.CONFIG_FILE_PATH);
			configProfile = StringUtils.isEmpty(System.getProperty(DataLabelingConstants.CONFIG_PROFILE))
					? config.getProperty(DataLabelingConstants.CONFIG_PROFILE)
					: System.getProperty(DataLabelingConstants.CONFIG_PROFILE);
			dpEndpoint = StringUtils.isEmpty(System.getProperty(DataLabelingConstants.DLS_DP_URL))
					? config.getProperty(DataLabelingConstants.DLS_DP_URL)
					: System.getProperty(DataLabelingConstants.DLS_DP_URL);
			datasetId = StringUtils.isEmpty(System.getProperty(DataLabelingConstants.DATASET_ID))
					? config.getProperty(DataLabelingConstants.DATASET_ID)
					: System.getProperty(DataLabelingConstants.DATASET_ID);
			mlModelType = StringUtils.isEmpty(System.getProperty(DataLabelingConstants.ML_MODEL_TYPE))
					? config.getProperty(DataLabelingConstants.ML_MODEL_TYPE)
					: System.getProperty(DataLabelingConstants.ML_MODEL_TYPE);
			customModelId = StringUtils.isEmpty(System.getProperty(DataLabelingConstants.CUSTOM_MODEL_ID))
					? config.getProperty(DataLabelingConstants.CUSTOM_MODEL_ID)
					: System.getProperty(DataLabelingConstants.CUSTOM_MODEL_ID);
			labelingAlgorithm = StringUtils.isEmpty(System.getProperty(DataLabelingConstants.LABELING_ALGORITHM))
					? config.getProperty(DataLabelingConstants.LABELING_ALGORITHM)
					: System.getProperty(DataLabelingConstants.LABELING_ALGORITHM);
			String threadConfig = StringUtils.isEmpty(System.getProperty(DataLabelingConstants.THREAD_COUNT))
					? config.getProperty(DataLabelingConstants.THREAD_COUNT)
					: System.getProperty(DataLabelingConstants.THREAD_COUNT);
			threadCount = (!threadConfig.isEmpty()) ? Integer.parseInt(threadConfig)
					: DataLabelingConstants.DEFAULT_THREAD_COUNT;
			performAssertionOninput();
			initializeLabelingStrategy();
			validateAndInitializeLabels(config);
			dlsDpClient = initializeDpClient();
			aiLanguageClient = initializeLanguageClient();
			aiVisionClient = initializeVisionClient();
			objectStorageClient = initializeObjectStorageClient();
		} catch (IOException ex) {
			ExceptionUtils.wrapAndThrow(ex);
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

		case "ML_ASSISTED_IMAGE_CLASSIFICATION":
			labelingStrategy = new MlAssistedImageClassification();
			break;

		case "ML_ASSISTED_TEXT_CLASSIFICATION":
			labelingStrategy = new MlAssistedTextClassification();
			break;

		case "ML_ASSISTED_OBJECT_DETECTION":
			labelingStrategy = new MlAssistedObjectDetection();
			break;

		case "ML_ASSISTED_ENTITY_EXTRACTION":
			labelingStrategy = new MlAssistedEntityExtraction();
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
//		case "ML_ASSISTED_IMAGE_CLASSIFICATION":
//			try {
//
//			}
//			catch () {
//
//			}
//		    break;
//		case "ML_ASSISTED_TEXT_CLASSIFICATION":
//			try {
//
//			}
//			catch () {
//
//			}
//			break;
//		case "ML_ASSISTED_OBJECT_DETECTION":
//			try {
//
//			}
//			catch () {
//
//			}
//			break;
//		case "ML_ASSISTED_ENTITY_EXTRACTION":
//			try {
//
//			}
//			catch () {
//
//			}
//			break;
		}

		if (labelingAlgorithm.equals("FIRST_REGEX_MATCH")) {
			regexPattern = StringUtils.isEmpty(System.getProperty(DataLabelingConstants.FIRST_MATCH_REGEX_PATTERN))
					? config.getProperty(DataLabelingConstants.FIRST_MATCH_REGEX_PATTERN)
					: System.getProperty(DataLabelingConstants.FIRST_MATCH_REGEX_PATTERN);
			pattern = Pattern.compile(regexPattern);
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
		dlsDpClient.setEndpoint(dpEndpoint);
		return dlsDpClient;
	}

	private AIServiceVisionClient initializeVisionClient() {
		ConfigFileReader.ConfigFile configFile = null;
		try {
			configFile = ConfigFileReader.parse(configFilePath, configProfile);
		} catch (IOException ioe) {
			log.error("Configuration file not found", ioe);
			ExceptionUtils.wrapAndThrow(ioe);
		}
		final AuthenticationDetailsProvider configFileProvider = new ConfigFileAuthenticationDetailsProvider(
				configFile);
		aiVisionClient = new AIServiceVisionClient(configFileProvider);
		aiVisionClient.setEndpoint(String.format(
				"https://vision.aiservice.%s.oci.oraclecloud.com",
				region));
		return aiVisionClient;
	}

	private AIServiceLanguageClient initializeLanguageClient() {
		ConfigFileReader.ConfigFile configFile = null;
		try {
			configFile = ConfigFileReader.parse(configFilePath, configProfile);
		} catch (IOException ioe) {
			log.error("Configuration file not found", ioe);
			ExceptionUtils.wrapAndThrow(ioe);
		}
		final AuthenticationDetailsProvider configFileProvider = new ConfigFileAuthenticationDetailsProvider(
				configFile);
		aiLanguageClient = new AIServiceLanguageClient(configFileProvider);
		aiLanguageClient.setEndpoint(String.format(
				"https://language.aiservice.%s.oci.oraclecloud.com",
				region));
		return aiLanguageClient;
	}

	private ObjectStorageClient initializeObjectStorageClient() {
		ConfigFileReader.ConfigFile configFile = null;
		try {
			configFile = ConfigFileReader.parse(configFilePath, configProfile);
		} catch (IOException ioe) {
			log.error("Configuration file not found", ioe);
			ExceptionUtils.wrapAndThrow(ioe);
		}
		final AuthenticationDetailsProvider configFileProvider = new ConfigFileAuthenticationDetailsProvider(
				configFile);
		objectStorageClient = new ObjectStorageClient(configFileProvider);
		objectStorageClient.setRegion(region);
		return objectStorageClient;
	}

	private void performAssertionOninput() {
		assert configFilePath != null : "Config filepath cannot be empty";
		assert configProfile != null : "Config Profile cannot be empty";
		assert dpEndpoint != null : "DLS DP URL cannot be empty";
		assert datasetId != null : "Dataset Id cannot be empty";
		assert labelingAlgorithm != null : "Labeling Strategy cannot be empty";
		assert threadCount >= 1 : "Invalid Thread Count Passed";
	}

}
