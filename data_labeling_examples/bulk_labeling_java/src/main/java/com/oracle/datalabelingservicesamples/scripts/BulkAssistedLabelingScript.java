package com.oracle.datalabelingservicesamples.scripts;

import java.security.InvalidParameterException;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.stream.Collectors;

import com.oracle.bmc.datalabelingservice.model.Dataset;
import com.oracle.bmc.datalabelingservice.model.ImageDatasetFormatDetails;
import com.oracle.bmc.datalabelingservice.model.Label;
import com.oracle.bmc.datalabelingservice.model.ObjectStorageSourceDetails;
import com.oracle.bmc.datalabelingservice.model.TextDatasetFormatDetails;
import com.oracle.bmc.datalabelingservice.requests.GetDatasetRequest;
import com.oracle.bmc.datalabelingservice.responses.GetDatasetResponse;
import com.oracle.bmc.datalabelingservicedataplane.model.Annotation;
import com.oracle.datalabelingservicesamples.constants.DataLabelingConstants;
import com.oracle.datalabelingservicesamples.labelingstrategies.MlAssistedLabelingStrategy;
import com.oracle.datalabelingservicesamples.labelingstrategies.MlAssistedEntityExtraction;
import com.oracle.datalabelingservicesamples.labelingstrategies.MlAssistedImageClassification;
import com.oracle.datalabelingservicesamples.labelingstrategies.MlAssistedObjectDetection;
import com.oracle.datalabelingservicesamples.labelingstrategies.MlAssistedTextClassification;
import com.oracle.datalabelingservicesamples.modelTraining.ModelTrainingLanguageWrapper;
import com.oracle.datalabelingservicesamples.modelTraining.ModelTrainingVisionWrapper;
import com.oracle.datalabelingservicesamples.modelTraining.ModelTrainingWrapper;
import com.oracle.datalabelingservicesamples.requests.AssistedLabelingParams;
import com.oracle.datalabelingservicesamples.requests.BucketDetails;
import com.oracle.datalabelingservicesamples.requests.ModelTrainingParams;
import com.oracle.datalabelingservicesamples.tasks.TaskHandler;
import com.oracle.datalabelingservicesamples.tasks.TaskProvider;
import com.oracle.datalabelingservicesamples.utils.DataPlaneAPIWrapper;
import org.apache.commons.collections4.ListUtils;

import com.oracle.bmc.datalabelingservicedataplane.model.CreateAnnotationDetails;
import com.oracle.bmc.datalabelingservicedataplane.model.RecordSummary;
import com.oracle.datalabelingservicesamples.requests.Config;

import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang3.StringUtils;

import static java.lang.Float.parseFloat;

/*
 *
 * This Script takes following input for Assisted Labeling:
 *
 * DATASET_ID : the id of the dataset that you want to bulk label
 * ML_MODEL_TYPE : String input specifying whether to use Pretrained/Custom models for the ai services
 * LABELING_ALGORITHM : The algorithm that will determine the label of any record.
 * 						Currently following algorithms are supported: ML_ASSISTED_IMAGE_CLASSIFICATION
 *                                                                    ML_ASSISTED_TEXT_CLASSIFICATION
 *                                                                    ML_ASSISTED_OBJECT_DETECTION
 *                                                                    ML_ASSISTED_ENTITY_EXTRACTION
 *
 *
 * Following code constraints are added:
 * 	1. The API only annotates unlabeled records. Labels that are already annotated will be skipped.
 *
 */
@Slf4j
public class BulkAssistedLabelingScript {

    static ExecutorService executorService;
    static ExecutorService annotationExecutorService;
    static Dataset dataset;
    private static AssistedLabelingParams assistedLabelingParams;
    private static final TaskHandler taskHandler = new TaskHandler(new TaskProvider());
    private static final DataPlaneAPIWrapper dataPlaneAPIWrapper = new DataPlaneAPIWrapper();
    private static MlAssistedLabelingStrategy mlAssistedLabelingStrategy = null;
    private static ModelTrainingWrapper modelTrainingWrapper = null;
    static List<String> successRecordIds = Collections.synchronizedList(new ArrayList<String>());
    static List<String> failedRecordIds = Collections.synchronizedList(new ArrayList<String>());

    static {
        executorService = Executors.newFixedThreadPool(Config.INSTANCE.getThreadCount());
        annotationExecutorService = Executors.newFixedThreadPool(Config.INSTANCE.getThreadCount());
    }

    public static void main(String[] args) throws InterruptedException, ExecutionException {
        long startTime = System.nanoTime();
        String datasetId = Config.INSTANCE.getDatasetId();
        initializeAssistedLabelingParams(datasetId);
        DataPlaneAPIWrapper dpAPIWrapper = new DataPlaneAPIWrapper();

        // Initialize parameters required for bulk assisted labeling
        float confidenceScore = parseFloat(Config.INSTANCE.getConfidenceThreshold());

        ObjectStorageSourceDetails sourceDetails = (ObjectStorageSourceDetails) dataset.getDatasetSourceDetails();

        List<String> dlsDatasetLabels = new ArrayList<>();
        try {
            dataset.getLabelSet().getItems().stream()
                    .forEach(
                            LabelName -> {
                                dlsDatasetLabels.add(LabelName.getName());
                            });
        } catch (Exception e) {
            log.error("Exception in getting labels from dataset {}", datasetId);
            return;
        }

        assistedLabelingParams = AssistedLabelingParams.builder()
                .datasetId(datasetId)
                .compartmentId(dataset.getCompartmentId())
                .annotationFormat(dataset.getAnnotationFormat())
                .assistedLabelingTimeout(DataLabelingConstants.ASSISTED_LABELING_TIMEOUT)
                .mlModelType(Config.INSTANCE.getMlModelType())
                .customModelId(Config.INSTANCE.getMlModelType().equals("CUSTOM") ? Config.INSTANCE.getCustomModelId() : null)
                .confidenceThreshold(confidenceScore)
                .dlsDatasetLabels(dlsDatasetLabels)
                .customerBucket(BucketDetails.builder()
                        .bucketName(sourceDetails.getBucket())
                        .namespace(sourceDetails.getNamespace())
                        .prefix(sourceDetails.getPrefix())
                        .region(Config.INSTANCE.getRegion())
                        .build())
                .modelTrainingParams(ModelTrainingParams.builder()
                .modelTrainingProjectId(Config.INSTANCE.getModelTrainingProjectId())
                .customTrainingEnabled(Config.INSTANCE.getCustomTrainingEnabled().equals("true"))
                        .build())
                .build();

        if(Config.INSTANCE.getCustomTrainingEnabled().equalsIgnoreCase("true")){
            log.info("Custom model training is enabled, starting the training flow.");
            initializeCustomTrainingParams(assistedLabelingParams);
            try {
                modelTrainingWrapper.performModelTraining(assistedLabelingParams);
            } catch (Exception e) {
                log.info("Failed to train model for project Id : {} dataset Id : {}", assistedLabelingParams.getModelTrainingParams().getModelTrainingProjectId(), assistedLabelingParams.getDatasetId());
            }
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
            log.info("Create annotation failed for record Ids {}", failedRecordIds);
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
                        mlAssistedLabelingStrategy,
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
                    successRecordIds.add(annotation.getRecordId());
                },
                exception -> {
                    if(exception.getMessage().contains("recordId")){
                        failedRecordIds.add(StringUtils.substringAfter(exception.getMessage(), "recordId: "));
                    }

                    // TODO - Changes required here
                    //                    if (exception.getCause() instanceof BmcException) {
                    //                        BmcException bmcException = (BmcException)
                },
                assistedLabelingParams.getAssistedLabelingTimeout());
    }

    private static void initializeAssistedLabelingParams(String datasetId) {
        /*
         * Validate Dataset
         */
        GetDatasetRequest getDatasetRequest = GetDatasetRequest.builder().datasetId(datasetId).build();
        GetDatasetResponse datasetResponse = Config.INSTANCE.getDlsCpClient().getDataset(getDatasetRequest);
        assert datasetResponse.get__httpStatusCode__() == 200 : "Invalid Dataset Id Provided";
        List<Label> datasetLabelSet = datasetResponse.getDataset().getLabelSet().getItems();

        /*
         * Validate Input Label Set
         */
        Set<String> actualLabels = new HashSet<>();
        for (Label labelName : datasetLabelSet) {
            actualLabels.add(labelName.getName());
        }

        /*
         * Validate custom model id
         */
        if (Config.INSTANCE.getMlModelType().equals("CUSTOM")) {
            if(Config.INSTANCE.getCustomModelId().isEmpty()) {
                log.error("Custom model ID cannot be empty when ML model type is custom");
                throw new InvalidParameterException("Custom model ID cannot be empty");
            }
        }

        dataset = datasetResponse.getDataset();

        /*
         * Initialise labeling algorithm
         */
        String labelingAlgorithm = Config.INSTANCE.getLabelingAlgorithm();
        if(!labelingAlgorithm.equals("ML_ASSISTED_LABELING")){
            log.error("Invalid algorithm for ML assisted labeling");
            throw new InvalidParameterException("Invalid algorithm for ML assisted labeling");
        }

        if(dataset.getDatasetFormatDetails() instanceof ImageDatasetFormatDetails) {
            if (dataset.getAnnotationFormat().equals("SINGLE_LABEL") || dataset.getAnnotationFormat().equals("MULTI_LABEL")) {
                mlAssistedLabelingStrategy = new MlAssistedImageClassification();
            } else if (dataset.getAnnotationFormat().equals("OBJECT_DETECTION")) {
                mlAssistedLabelingStrategy = new MlAssistedObjectDetection();
            }
            else{
                log.error("Invalid annotation format for ML assisted labeling");
                throw new InvalidParameterException("Invalid annotation format for ML assisted labeling");
            }
        }
        else if(dataset.getDatasetFormatDetails() instanceof TextDatasetFormatDetails){
            if(dataset.getAnnotationFormat().equals("SINGLE_LABEL")||dataset.getAnnotationFormat().equals("MULTI_LABEL")) {
                mlAssistedLabelingStrategy = new MlAssistedTextClassification();
            }
            else if(dataset.getAnnotationFormat().equals("ENTITY_EXTRACTION")){
                mlAssistedLabelingStrategy = new MlAssistedEntityExtraction();
            }
            else{
                log.error("Invalid annotation format for ML assisted labeling");
                throw new InvalidParameterException("Invalid annotation format for ML assisted labeling");
            }
        }
        else{
            log.error("Invalid dataset format type for ML assisted labeling");
            throw new InvalidParameterException("Invalid dataset format type for ML assisted labeling");
        }
    }

    private static void initializeCustomTrainingParams(AssistedLabelingParams assistedLabelingParams) {

        /*
         * initialise model training wrapper
         */
        if(dataset.getDatasetFormatDetails() instanceof ImageDatasetFormatDetails) {
            modelTrainingWrapper = new ModelTrainingVisionWrapper();
            if (dataset.getAnnotationFormat().equals("SINGLE_LABEL") || dataset.getAnnotationFormat().equals("MULTI_LABEL")) {
                assistedLabelingParams.getModelTrainingParams().setModelTrainingType("IMAGE_CLASSIFICATION");
            } else if (dataset.getAnnotationFormat().equals("OBJECT_DETECTION")) {
                assistedLabelingParams.getModelTrainingParams().setModelTrainingType("OBJECT_DETECTION");
            }
            else{
                log.error("Invalid annotation format for model training in vision");
                throw new InvalidParameterException("Invalid annotation format for model training in vision");
            }
        }
        else if(dataset.getDatasetFormatDetails() instanceof TextDatasetFormatDetails){
            modelTrainingWrapper = new ModelTrainingLanguageWrapper();
            if(dataset.getAnnotationFormat().equals("SINGLE_LABEL")||dataset.getAnnotationFormat().equals("MULTI_LABEL")) {
                assistedLabelingParams.getModelTrainingParams().setModelTrainingType("TEXT_CLASSIFICATION");
            }
            else if(dataset.getAnnotationFormat().equals("ENTITY_EXTRACTION")){
                assistedLabelingParams.getModelTrainingParams().setModelTrainingType("NAMED_ENTITY_RECOGNITION");
            }
            else{
                log.error("Invalid annotation format for model training in language");
                throw new InvalidParameterException("Invalid annotation format for model training in language");
            }
        }
        else{
            log.error("Invalid dataset format type for ML assisted labeling");
            throw new InvalidParameterException("Invalid dataset format type for ML assisted labeling");
        }
    }
}
