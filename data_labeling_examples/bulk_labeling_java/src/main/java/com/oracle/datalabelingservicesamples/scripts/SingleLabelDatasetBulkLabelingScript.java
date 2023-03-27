package com.oracle.datalabelingservicesamples.scripts;

import java.security.InvalidParameterException;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

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

import com.oracle.datalabelingservicesamples.requests.DLSScript;
import lombok.extern.slf4j.Slf4j;

/*
 * 
 * This Script takes following input for Bulk Labeling:
 * 
 * DATASET_ID : the id of the dataset that you want to bulk label
 * LABELS : List of labels against which the record names will be matched
 * LABELING_ALGORITHM : The pattern matching algorithm that will determine the label of any record. 
 * 						Currently following algorithms are supported: FIRST_LETTER and FIRST_MATCH
 * FIRST_MATCH_REGEX_PATTERN : When the labeling algorithm is FIRST_MATCH, then we match against this pattern
 * 
 */

@Slf4j
public class SingleLabelDatasetBulkLabelingScript extends DLSScript {

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
		validateRequest(datasetId);

		log.info("Starting Bulk Labeling for dataset: {}", dataset.getDisplayName());
		Boolean isUnlabeledRecordAvailable = true;
		int recordCount = 0;
		String page = null;
		do {
			ListRecordsRequest listRecordsRequest = ListRecordsRequest.builder().datasetId(datasetId)
					.compartmentId(dataset.getCompartmentId()).lifecycleState(LifecycleState.Active).isLabeled(false).page(page)
					.limit(DataLabelingConstants.MAX_LIST_RECORDS_LIMITS).build();
			ListRecordsResponse response = Config.INSTANCE.getDlsDpClient().listRecords(listRecordsRequest);
			assert response.get__httpStatusCode__() == 200 : "List Record Response Error";
			recordCount += response.getRecordCollection().getItems().size();
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
			page = response.getOpcNextPage();
		}while(page != null);

		executorService.shutdown();
		log.info("Time Taken for datasetId {}", datasetId);
		log.info("Total Records Processed {}", recordCount);
		log.info("Successfully Annotated {} record Ids", successRecordIds.size());
		log.info("Failed record Ids {}", failedRecordIds);
		long elapsedTime = System.nanoTime() - startTime;
		log.info("Time Taken for datasetId {} is {} seconds", datasetId, elapsedTime/ 1_000_000_000);
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

	private static void validateRequest(String datasetId) {
		/*
		 * Validate Dataset
		 */
		GetDatasetRequest getDatasetRequest = GetDatasetRequest.builder().datasetId(datasetId).build();
		GetDatasetResponse datasetResponse = Config.INSTANCE.getDlsDpClient().getDataset(getDatasetRequest);
		assert datasetResponse.get__httpStatusCode__() == 200 : "Invalid Dataset Id Provided";
		List<LabelName> datasetLabelSet = datasetResponse.getDataset().getLabelSet().getItems();

		/*
		 * Validate Input Label Set
		 */
		Set<String> actualLabels = new HashSet<>();
		for (LabelName labelName : datasetLabelSet) {
			actualLabels.add(labelName.getName());
		}

		for (String inputLabel : Config.INSTANCE.getLabels()) {
			if (!actualLabels.contains(inputLabel)) {
				log.error("Invalid Labels Provided {}", inputLabel);
				throw new InvalidParameterException("Invalid Input Label Set Provided");
			}
		}
		dataset = datasetResponse.getDataset();

	}

}
