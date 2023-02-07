package com.oracle.datalabelingservicesamples.scripts;

import java.security.InvalidParameterException;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Map.Entry;
import java.util.Set;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

import com.oracle.datalabelingservicesamples.requests.DLSScript;
import org.apache.commons.lang3.StringUtils;

import com.oracle.bmc.datalabelingservicedataplane.model.CreateAnnotationDetails;
import com.oracle.bmc.datalabelingservicedataplane.model.Dataset;
import com.oracle.bmc.datalabelingservicedataplane.model.Entity;
import com.oracle.bmc.datalabelingservicedataplane.model.GenericEntity;
import com.oracle.bmc.datalabelingservicedataplane.model.Label;
import com.oracle.bmc.datalabelingservicedataplane.model.LabelName;
import com.oracle.bmc.datalabelingservicedataplane.model.Record.LifecycleState;
import com.oracle.bmc.datalabelingservicedataplane.model.RecordSummary;
import com.oracle.bmc.datalabelingservicedataplane.requests.CreateAnnotationRequest;
import com.oracle.bmc.datalabelingservicedataplane.requests.GetDatasetRequest;
import com.oracle.bmc.datalabelingservicedataplane.requests.ListRecordsRequest;
import com.oracle.bmc.datalabelingservicedataplane.responses.GetDatasetResponse;
import com.oracle.bmc.datalabelingservicedataplane.responses.ListRecordsResponse;
import com.oracle.datalabelingservicesamples.constants.DataLabelingConstants;
import com.oracle.datalabelingservicesamples.requests.Config;

import lombok.extern.slf4j.Slf4j;

/*
 * 
 * This Script takes following input for Bulk Labeling:
 * 
 * DATASET_ID : the id of the dataset that you want to bulk label
 * CUSTOM_LABELS : JSON input specifying the labels to be applied for a object storage path.
 * 					Ex: { "dog/": ["dog"], "cat/": ["cat"] }
 * LABELING_ALGORITHM : The pattern matching algorithm that will determine the label of any record. 
 * 						Currently following algorithms are supported: CUSTOM_LABELS_MATCH
 * 
 * 
 * Following code constraints are added:
 * 	1. At max 3 distinct path is accepted 
 *	2. No nested path is allowed. Only top-level path is considered.
 *	 In case the user wants nested folder support, he/she can place the nested folder at top level to use this API.
 * 	3. The API only annotates unlabeled records. Labels that are already annotated will be skipped.
 * 
 */
@Slf4j
public class CustomBulkLabelingScript extends DLSScript {

	static ExecutorService executorService;
	static Dataset dataset;
	static List<String> successRecordIds = Collections.synchronizedList(new ArrayList<String>());
	static List<String> failedRecordIds = Collections.synchronizedList(new ArrayList<String>());

	static {
		executorService = Executors.newFixedThreadPool(Config.INSTANCE.getThreadCount());
	}

	public static void main(String[] args) throws InterruptedException, ExecutionException {
		long startTime = System.nanoTime();
		String datasetId = Config.INSTANCE.getDatasetId();
		Map<String, List<String>> bulkLabelingRequest = Config.INSTANCE.getCustomLabels();
		validateRequest(datasetId, bulkLabelingRequest);
		log.info("Starting Bulk Labeling for dataset: {}", dataset.getDisplayName());
		Boolean isUnlabeledRecordAvailable = true;
		String page = null;

		while (isUnlabeledRecordAvailable) {
			ListRecordsRequest listRecordsRequest = ListRecordsRequest.builder().datasetId(datasetId)
					.compartmentId(dataset.getCompartmentId()).lifecycleState(LifecycleState.Active).page(page)
					.limit(DataLabelingConstants.MAX_LIST_RECORDS_LIMITS).build();
			ListRecordsResponse response = Config.INSTANCE.getDlsDpClient().listRecords(listRecordsRequest);
			assert response.get__httpStatusCode__() == 200 : "List Record Response Error";

			if (response.getRecordCollection().getItems().size() > 0) {
				List<CompletableFuture<Void>> completableFutures = new ArrayList<>();
				for (RecordSummary record : response.getRecordCollection().getItems()) {
					List<String> label = Config.INSTANCE.getRuleBasedLabelingStrategy().getLabel(record);
					if (null != label) {
						CompletableFuture<Void> future = CompletableFuture
								.runAsync(() -> processAnnotationForRecord(record, label), executorService);
						completableFutures.add(future);
					} else {
						log.error("Label is null for record {}",record);
						failedRecordIds.add(record.getId());
					}
				}
				CompletableFuture<Void> combinedFuture = CompletableFuture
						.allOf(completableFutures.toArray(new CompletableFuture[0]));
				combinedFuture.get();
			}

			if (null == response.getOpcNextPage()) {
				isUnlabeledRecordAvailable = false;
			} else {
				page = response.getOpcNextPage();
			}

		}

		executorService.shutdown();
		log.info("Time Taken for datasetId {}", datasetId);
		log.info("Successfully Annotated {} record Ids", successRecordIds.size());
		log.info("Failed record Ids {}", failedRecordIds);
		long elapsedTime = System.nanoTime() - startTime;
		log.info("Time Taken for datasetId {} is {} seconds", datasetId, elapsedTime / 1_000_000_000);
	}

	private static void processAnnotationForRecord(RecordSummary record, List<String> labels) {
		try {
			List<Label> annotationLabel = new ArrayList<>();
			for (String label : labels) {
				annotationLabel.add(Label.builder().label(label).build());
			}
			List<Entity> entities = new ArrayList<>(
					Collections.singleton(GenericEntity.builder().labels(annotationLabel).build()));

			CreateAnnotationDetails annotationDetails = CreateAnnotationDetails.builder()
					.compartmentId(record.getCompartmentId()).recordId(record.getId()).entities(entities).build();
			CreateAnnotationRequest annotationReq = CreateAnnotationRequest.builder()
					.createAnnotationDetails(annotationDetails).build();
			Config.INSTANCE.getDlsDpClient().createAnnotation(annotationReq);
			successRecordIds.add(record.getId());
		} catch (Exception e) {
			log.error("Exception in creating annotation for record {}", record);
			failedRecordIds.add(record.getId());
		}
	}

	private static void validateRequest(String datasetId, Map<String, List<String>> bulkLabelingRequest) {
		/*
		 * Validate Dataset
		 */
		GetDatasetRequest getDatasetRequest = GetDatasetRequest.builder().datasetId(datasetId).build();
		GetDatasetResponse datasetResponse = Config.INSTANCE.getDlsDpClient().getDataset(getDatasetRequest);
		assert datasetResponse.get__httpStatusCode__() == 200 : "Invalid Dataset Id Provided";
		List<LabelName> datasetLabelSet = datasetResponse.getDataset().getLabelSet().getItems();

		/*
		 * Validate Request
		 */
		if (bulkLabelingRequest.size() > 3) {
			log.error("More than allowed limit of 3 paths were provided");
			throw new InvalidParameterException("More than allowed limit of 3 paths were provided");
		}

		/*
		 * Validate Input Label Set
		 */
		Set<String> actualLabels = new HashSet<>();
		for (LabelName labelName : datasetLabelSet) {
			actualLabels.add(labelName.getName());
		}

		for (Entry<String, List<String>> requestEntry : bulkLabelingRequest.entrySet()) {

			if (StringUtils.countMatches(requestEntry.getKey(), "/") != 1) {
				log.error("Invalid Path Name provided {}", requestEntry.getKey());
				throw new InvalidParameterException("Invalid Path Name Provided");
			}
			for (String label : requestEntry.getValue()) {
				if (!actualLabels.contains(label)) {
					log.error("Invalid Labels Provided {}", label);
					throw new InvalidParameterException("Invalid Input Label Provided");
				}
			}
		}

		dataset = datasetResponse.getDataset();

	}
}
