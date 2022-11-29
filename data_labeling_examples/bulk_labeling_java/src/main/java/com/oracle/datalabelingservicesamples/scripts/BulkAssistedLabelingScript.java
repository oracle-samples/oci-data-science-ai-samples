package com.oracle.datalabelingservicesamples.scripts;

import java.security.InvalidParameterException;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Map.Entry;
import java.util.Set;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.stream.Collectors;

import com.oracle.bmc.datalabelingservice.model.ObjectStorageSourceDetails;
import com.oracle.bmc.datalabelingservicedataplane.model.Annotation;
import com.oracle.datalabelingservicesamples.constants.DataLabelingConstants;
import com.oracle.datalabelingservicesamples.labelingstrategies.AssistedLabelingStrategy;
import com.oracle.datalabelingservicesamples.requests.AssistedLabelingParams;
import com.oracle.datalabelingservicesamples.requests.BucketDetails;
import com.oracle.datalabelingservicesamples.tasks.TaskHandler;
import com.oracle.datalabelingservicesamples.tasks.TaskProvider;
import com.oracle.datalabelingservicesamples.utils.DataPlaneAPIWrapper;
import org.apache.commons.collections4.ListUtils;
import org.apache.commons.lang3.StringUtils;

import com.oracle.bmc.datalabelingservicedataplane.model.CreateAnnotationDetails;
import com.oracle.bmc.datalabelingservicedataplane.model.Dataset;
import com.oracle.bmc.datalabelingservicedataplane.model.LabelName;
import com.oracle.bmc.datalabelingservicedataplane.model.RecordSummary;
import com.oracle.bmc.datalabelingservicedataplane.requests.GetDatasetRequest;
import com.oracle.bmc.datalabelingservicedataplane.responses.GetDatasetResponse;
import com.oracle.datalabelingservicesamples.requests.Config;

import lombok.extern.slf4j.Slf4j;

/*
 *
 * This Script takes following input for Assisted Labeling:
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
public class BulkAssistedLabelingScript {

    static ExecutorService executorService;
    static ExecutorService annotationExecutorService;
    static Dataset dataset;
    private static AssistedLabelingParams assistedLabelingParams  = new AssistedLabelingParams();
    private static final TaskHandler taskHandler = new TaskHandler(new TaskProvider());
    private static final DataPlaneAPIWrapper dataPlaneAPIWrapper = new DataPlaneAPIWrapper();
    private static final AssistedLabelingStrategy assistedLabelingStrategy = (AssistedLabelingStrategy) Config.INSTANCE.getLabelingStrategy();
    static List<String> successRecordIds = Collections.synchronizedList(new ArrayList<String>());
    static List<String> failedRecordIds = Collections.synchronizedList(new ArrayList<String>());

    static {
        executorService = Executors.newFixedThreadPool(Config.INSTANCE.getThreadCount());
        annotationExecutorService = Executors.newFixedThreadPool(Config.INSTANCE.getThreadCount());
    }

    public static void main(String[] args) throws InterruptedException, ExecutionException {
        long startTime = System.nanoTime();
        String datasetId = Config.INSTANCE.getDatasetId();
//        TODO - validation changes
//        Map<String, List<String>> bulkLabelingRequest = Config.INSTANCE.getCustomLabels();
//        validateRequest(datasetId, bulkLabelingRequest);
        DataPlaneAPIWrapper dpAPIWrapper = new DataPlaneAPIWrapper();

//        Initialize parameters required for bulk assisted labeling
        assistedLabelingParams.setAssistedLabelingTimeout(DataLabelingConstants.ASSISTED_LABELING_TIMEOUT);
        assistedLabelingParams.setCompartmentId(Config.INSTANCE.getCompartmentId());
        com.oracle.bmc.datalabelingservice.model.Dataset dataset = Config.INSTANCE.getDlsCpClient().getDataset(com.oracle.bmc.datalabelingservice.requests.GetDatasetRequest.builder()
                .datasetId(datasetId)
                .build())
                .getDataset();

        ObjectStorageSourceDetails sourceDetails = (ObjectStorageSourceDetails) dataset.getDatasetSourceDetails();

        assistedLabelingParams.setCustomerBucket(BucketDetails.builder()
                .bucketName(sourceDetails.getBucket())
                .namespace(sourceDetails.getNamespace())
                .prefix(sourceDetails.getPrefix())
                .region(Config.INSTANCE.getRegion())
                .build());
        assistedLabelingParams.setMlModelType(Config.INSTANCE.getMlModelType());
        switch (Config.INSTANCE.getMlModelType()) {
            case "CUSTOM":
                assistedLabelingParams.setCustomModelId(Config.INSTANCE.getCustomModelId());
                break;
            case "PRETRAINED":
                assistedLabelingParams.setCustomModelId(null);
                break;
        }

        List<String> dlsDatasetLabels = new ArrayList<>();
        try {
            dataset.getLabelSet().getItems().stream()
                    .forEach(
                            LabelName -> {
                                dlsDatasetLabels.add(LabelName.getName());
                            });
            assistedLabelingParams.setDlsDatasetLabels(dlsDatasetLabels);
        } catch (Exception e) {
            log.error("Exception in getting labels from dataset {}", datasetId);
            return;
        }

        log.info("Starting Assisted Labeling for dataset: {}", dataset.getDisplayName());

        // 1. List existing record files
        log.info("List Dataset Records");
        List<RecordSummary> existingRecords = null;
        try {
            existingRecords =
                    dpAPIWrapper.listRecords(
                            datasetId,
                            dataset.getCompartmentId(),
                            true);
            log.info(
                    "For dataset {}, found {} existing records.",
                    datasetId,
                    existingRecords.size());
        } catch (Exception e) {
            log.error(
                    "Failed to list existing records for dataset",
                    e);
        }

        // 2. Get unlabelled records
        List<RecordSummary> recordsForAssistedLabelling =
                existingRecords.stream()
                        .filter(
                                recordSummary ->
                                        !recordSummary.getIsLabeled())
                        .collect(Collectors.toList());

        // 3. Create batch requests to downstream AI service for predictions
        int maxDownstreamBatchrequest = 8;
        List<List<RecordSummary>> recordRequestsInBatches =
                ListUtils.partition(recordsForAssistedLabelling, maxDownstreamBatchrequest);

        try {
            createAndWaitForAssistedLabelTasks(recordRequestsInBatches, assistedLabelingParams, executorService);
            executorService.shutdown();
            annotationExecutorService.shutdown();
            log.info("Time Taken for datasetId {}", datasetId);
            log.info("Successfully Annotated {} record Ids", successRecordIds.size());
            log.info("Failed record Ids {}", failedRecordIds);
            long elapsedTime = System.nanoTime() - startTime;
            log.info("Time Taken for datasetId {} is {} seconds", datasetId, elapsedTime / 1_000_000_000);
        } catch (Exception e) {
            log.error(
                    "Failed while making downstream API calls",
                    e);
        }
}

    private static void createAndWaitForAssistedLabelTasks(
            List<List<RecordSummary>> recordSummaries,
            AssistedLabelingParams assistedLabelingParams,
            ExecutorService executorService) {
        List<Future<List<CreateAnnotationDetails>>> getAssistedLabellingTasks =
                taskHandler.getAssistedLabelTasks(
                        recordSummaries,
                        assistedLabelingParams,
                        assistedLabelingStrategy,
                        executorService);

        List<CreateAnnotationDetails> createAnnotationDetailsList = new ArrayList<>();
        taskHandler.waitForTasks(
                getAssistedLabellingTasks,
                createAnnotationDetailsResponse -> {
                    if (createAnnotationDetailsResponse != null
                            && !createAnnotationDetailsResponse.isEmpty()) {
                        createAnnotationDetailsList.addAll(createAnnotationDetailsResponse);
                        log.info(
                                "createAnnotationDetailsList size : {}",
                                createAnnotationDetailsList.size());
                    }
                },
                exception -> {
                    // TODO - Changes required here
                    //                    if (exception.getCause() instanceof BmcException) {
                    //                        BmcException bmcException = (BmcException)
                },
                assistedLabelingParams.getAssistedLabelingTimeout());
        log.info("Coming here after thread finished");
        createAndWaitForAnnotationTasksToComplete(createAnnotationDetailsList);
    }

    private static void createAndWaitForAnnotationTasksToComplete(
            List<CreateAnnotationDetails> createAnnotationDetailsList) {
        List<Future<Annotation>> createAnnotationTasks =
                taskHandler.getCreateAnnotationTasks(
                        createAnnotationDetailsList,
                        dataPlaneAPIWrapper,
                        "opcRequestId",
                        annotationExecutorService);
        taskHandler.waitForTasks(
                createAnnotationTasks,
                annotation -> {
                    log.info(
                            "Assisted labels for {} created successfully. Record Id :{}",
                            annotation.getRecordId(),
                            annotation.getId());
                },
                exception -> {
                    // TODO - Changes required here
                    //                    if (exception.getCause() instanceof BmcException) {
                    //                        BmcException bmcException = (BmcException)
                },
                assistedLabelingParams.getAssistedLabelingTimeout());

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
