package com.oracle.datalabelingservicesamples.scripts;

import java.security.InvalidParameterException;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.stream.Collectors;

import com.google.common.collect.ImmutableSet;
import com.oracle.bmc.datalabelingservice.model.Dataset;
import com.oracle.bmc.datalabelingservice.model.DelimitedFileTypeMetadata;
import com.oracle.bmc.datalabelingservice.model.ExportFormat;
import com.oracle.bmc.datalabelingservice.model.ImageDatasetFormatDetails;
import com.oracle.bmc.datalabelingservice.model.ObjectStorageSnapshotExportDetails;
import com.oracle.bmc.datalabelingservice.model.ObjectStorageSourceDetails;
import com.oracle.bmc.datalabelingservice.model.TextDatasetFormatDetails;
import com.oracle.bmc.datalabelingservice.model.UpdateDatasetDetails;
import com.oracle.bmc.datalabelingservice.requests.GetDatasetRequest;
import com.oracle.bmc.datalabelingservice.requests.UpdateDatasetRequest;
import com.oracle.bmc.datalabelingservice.responses.GetDatasetResponse;
import com.oracle.bmc.datalabelingservice.responses.UpdateDatasetResponse;
import com.oracle.bmc.datalabelingservicedataplane.model.Annotation;
import com.oracle.bmc.model.BmcException;
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
import com.oracle.datalabelingservicesamples.requests.DLSScript;
import com.oracle.datalabelingservicesamples.requests.ModelTrainingParams;
import com.oracle.datalabelingservicesamples.requests.SnapshotDatasetParams;
import com.oracle.datalabelingservicesamples.tasks.TaskHandler;
import com.oracle.datalabelingservicesamples.tasks.TaskProvider;
import com.oracle.datalabelingservicesamples.utils.DlsApiWrapper;
import com.oracle.datalabelingservicesamples.utils.InputValidator;
import com.oracle.pic.commons.util.EntityType;
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
 * LABELING_ALGORITHM : The algorithm that will determine the label of any record. ML_ASSISTED_LABELING
 * 						Currently following annotation types are supported: Single/Multi Label Image Classification
     *                                                                      Single Label Text Classification
 *                                                                          Image Object Detection
 *                                                                          Text Named Entity Extraction
 *
 *
 * Following code constraints are added:
 * 	1. The API only annotates unlabeled records. Labels that are already annotated will be skipped.
 *
 */
@Slf4j
public class BulkAssistedLabelingScript extends DLSScript {

    static ExecutorService executorService;
    static ExecutorService annotationExecutorService;
    static Dataset dataset;
    private static AssistedLabelingParams assistedLabelingParams;
    private static final TaskHandler taskHandler = new TaskHandler(new TaskProvider());
    private static final DlsApiWrapper dlsApiWrapper = new DlsApiWrapper();
    private static final InputValidator inputValidator = new InputValidator();
    private static MlAssistedLabelingStrategy mlAssistedLabelingStrategy = null;
    private static ModelTrainingWrapper modelTrainingWrapper = null;
    static List<String> successRecordIds = Collections.synchronizedList(new ArrayList<String>());
    static List<String> failedRecordIds = Collections.synchronizedList(new ArrayList<String>());
    private static final Set<String> datasetEntityTypes =
            ImmutableSet.of(
                    EntityType.DataLabelingDataset.getName(),
                    EntityType.DataLabelingDatasetPre.getName(),
                    EntityType.DataLabelingDatasetDev.getName(),
                    EntityType.DataLabelingDatasetInt.getName());
    private static final Set<String> aiServiceModelTypes =
            ImmutableSet.of(
                    EntityType.AiVisionModel.getName(),
                    EntityType.AiLanguageModel.getName());
    private static final Set<String> aiServiceProjectTypes =
            ImmutableSet.of(
                    EntityType.AiVisionProject.getName(),
                    EntityType.AiLanguageProject.getName());

    static {
        executorService = Executors.newFixedThreadPool(Config.INSTANCE.getThreadCount());
        annotationExecutorService = Executors.newFixedThreadPool(Config.INSTANCE.getThreadCount());
    }

    public static void main(String[] args) throws Exception {
        long startTime = System.nanoTime();
        String datasetId = Config.INSTANCE.getDatasetId();
        validateAssistedLabelingParams();
        initializeAssistedLabelingParams(datasetId);

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
                .build();

        if(Config.INSTANCE.getMlModelType().equalsIgnoreCase("NEW")){
            log.info("Custom model training is enabled, starting the training flow.");
            validateCustomTrainingParams();
            initializeCustomTrainingParams(assistedLabelingParams);
            // Initialising the custom model id/endpoint as empty so that once model training is completed this field can be populated
            assistedLabelingParams.setCustomModelId("");
            assistedLabelingParams.setCustomModelEndpoint("");
            try {
                modelTrainingWrapper.performModelTraining(assistedLabelingParams);
            } catch (Exception e) {
                log.info("Failed to train model for project Id : {} dataset Id : {}", assistedLabelingParams.getModelTrainingParams().getModelTrainingProjectId(), assistedLabelingParams.getDatasetId());
                throw new Exception("Assisted labeling failed");
            }
        }

        log.info("Starting Assisted Labeling for dataset: {}", dataset.getDisplayName());

        // 1. List existing record files
        log.info("List Dataset Records");
        List<RecordSummary> existingRecords = null;
        try {
            existingRecords =
                    dlsApiWrapper.listRecords(
                            datasetId,
                            dataset.getCompartmentId(),
                            true);
            log.info(
                    "For dataset {}, found {} total records.",
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
        log.info(
                "For dataset {}, found {} unlabeled records.",
                datasetId,
                recordsForAssistedLabelling.size());

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

            // TODO - enable tag creation when required for storing model metadata
//            updateDatasetWithModelInfo(assistedLabelingParams);
            // TODO - delete the object storage files once labeling is complete
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
                    if (exception.getCause() instanceof BmcException) {
                        BmcException bmcException = (BmcException) exception;
                        log.error("Exception in Update Dataset API : {}", bmcException.getMessage());
                        log.error("Create annotation failed with status code : {}", bmcException.getStatusCode());
                    }
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
                        dlsApiWrapper,
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

    private static void validateAssistedLabelingParams(){
        inputValidator.validateRequiredParameter("ML model type", Config.INSTANCE.getMlModelType());
        inputValidator.validateMlModelType(Config.INSTANCE.getMlModelType());
        inputValidator.validateRequiredParameter("Labeling Algorithm", Config.INSTANCE.getLabelingAlgorithm());
        inputValidator.validateLabelingAlgorithm(Config.INSTANCE.getLabelingAlgorithm());
        inputValidator.validateRequiredParameter("Confidence Threshold", Config.INSTANCE.getConfidenceThreshold());
        inputValidator.validateConfidenceScoreThreshold(Config.INSTANCE.getConfidenceThreshold());
        inputValidator.isValidResourceOcid(Config.INSTANCE.getDatasetId(), datasetEntityTypes, "DLS dataset");

        /*
         * Validate custom model id
         */
        // TODO support custom models in different compartments than the dataset
        if (Config.INSTANCE.getMlModelType().equals("CUSTOM")) {
            if(Config.INSTANCE.getCustomModelId().isEmpty()) {
                log.error("Custom model ID cannot be empty when ML model type is custom");
                throw new InvalidParameterException("Custom model ID cannot be empty");
            }
            inputValidator.isValidResourceOcid(Config.INSTANCE.getCustomModelId(), aiServiceModelTypes, "custom ML model");
        }
    }

    private static void validateCustomTrainingParams(){
        // TODO Training dataset ids could be dls or some other input
        inputValidator.isValidResourceOcid(Config.INSTANCE.getTrainingDatasetId(), datasetEntityTypes, "training DLS dataset");
        if(!Config.INSTANCE.getModelTrainingProjectId().isEmpty()) {
            inputValidator.isValidResourceOcid(Config.INSTANCE.getModelTrainingProjectId(), aiServiceProjectTypes, "model training project");
        }
    }

    private static void initializeAssistedLabelingParams(String datasetId) {
        /*
         * Get Dataset
         */
        GetDatasetRequest getDatasetRequest = GetDatasetRequest.builder().datasetId(datasetId).build();
        GetDatasetResponse datasetResponse = Config.INSTANCE.getDlsCpClient().getDataset(getDatasetRequest);
        assert datasetResponse.get__httpStatusCode__() == 200 : "Invalid Dataset Id Provided";
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
            } else if (dataset.getAnnotationFormat().equals("BOUNDING_BOX")) {
                mlAssistedLabelingStrategy = new MlAssistedObjectDetection();
            }
            else{
                log.error("Invalid annotation format for ML assisted labeling");
                throw new InvalidParameterException("Invalid annotation format for ML assisted labeling");
            }
        }
        else if(dataset.getDatasetFormatDetails() instanceof TextDatasetFormatDetails){
            if(dataset.getAnnotationFormat().equals("SINGLE_LABEL")) {
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

        String modelTrainingType = null;
        /*
         * initialise model training wrapper
         */
        if(dataset.getDatasetFormatDetails() instanceof ImageDatasetFormatDetails) {
            modelTrainingWrapper = new ModelTrainingVisionWrapper();
            if (dataset.getAnnotationFormat().equals("SINGLE_LABEL") || dataset.getAnnotationFormat().equals("MULTI_LABEL")) {
                modelTrainingType = "IMAGE_CLASSIFICATION";
            } else if (dataset.getAnnotationFormat().equals("BOUNDING_BOX")) {
                modelTrainingType = "OBJECT_DETECTION";
            }
            else{
                log.error("Invalid annotation format for model training in vision");
                throw new InvalidParameterException("Invalid annotation format for model training in vision");
            }
        }
        else if(dataset.getDatasetFormatDetails() instanceof TextDatasetFormatDetails){
            modelTrainingWrapper = new ModelTrainingLanguageWrapper();
            if(dataset.getAnnotationFormat().equals("SINGLE_LABEL")) {
                modelTrainingType = "TEXT_CLASSIFICATION";
            }
            else if(dataset.getAnnotationFormat().equals("ENTITY_EXTRACTION")){
                modelTrainingType = "NAMED_ENTITY_RECOGNITION";
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

        assistedLabelingParams.setModelTrainingParams(
                ModelTrainingParams.builder()
                        .modelTrainingType(modelTrainingType)
                        .modelTrainingProjectId(Config.INSTANCE.getModelTrainingProjectId())
                        .customTrainingEnabled(Config.INSTANCE.getMlModelType().equals("NEW"))
                        .trainingDatasetId(Config.INSTANCE.getTrainingDatasetId())
                        .build());

        /*
         * Get Training Dataset
         */
        GetDatasetRequest getDatasetRequest = GetDatasetRequest.builder()
                .datasetId(assistedLabelingParams.getModelTrainingParams().getTrainingDatasetId())
                .build();
        GetDatasetResponse datasetResponse = Config.INSTANCE.getDlsCpClient().getDataset(getDatasetRequest);
        assert datasetResponse.get__httpStatusCode__() == 200 : "Invalid Dataset Id Provided";
        Dataset trainingDataset = datasetResponse.getDataset();

        /*
         * Get Snapshot Dataset bucket details
         */

        ObjectStorageSourceDetails trainingDatasetSourceDetails =
                (ObjectStorageSourceDetails) trainingDataset.getDatasetSourceDetails();

        ExportFormat exportFormat = null;

        if(trainingDataset.getDatasetFormatDetails() instanceof ImageDatasetFormatDetails) {
            exportFormat = ExportFormat.builder()
                    .name(ExportFormat.Name.JsonlConsolidated)
                    .build();
        }
        else if(trainingDataset.getDatasetFormatDetails() instanceof TextDatasetFormatDetails){
            TextDatasetFormatDetails trainingDatasetFormatDetails =
                    (TextDatasetFormatDetails) trainingDataset.getDatasetFormatDetails();
            if(trainingDatasetFormatDetails.getTextFileTypeMetadata() instanceof DelimitedFileTypeMetadata){
                exportFormat = ExportFormat.builder()
                        .name(ExportFormat.Name.JsonlCompactPlusContent)
                        .build();
            }
            else {
                exportFormat = ExportFormat.builder()
                        .name(ExportFormat.Name.JsonlConsolidated)
                        .build();
            }
        }

        SnapshotDatasetParams snapshotDatasetParams =
                SnapshotDatasetParams.builder()
                        .snapshotBucketDetails(
                                ObjectStorageSnapshotExportDetails.builder()
                                .bucket(trainingDatasetSourceDetails.getBucket())
                                .namespace(trainingDatasetSourceDetails.getNamespace())
                                .prefix(trainingDatasetSourceDetails.getPrefix())
                                .build())
                        .snapshotDatasetId(trainingDataset.getId())
                        .exportFormat(exportFormat)
                        .build();

        assistedLabelingParams.setSnapshotDatasetParams(snapshotDatasetParams);
    }

    private static void updateDatasetWithModelInfo(AssistedLabelingParams assistedLabelingParams){

        /*
         * Get Dataset
         */
        GetDatasetRequest getDatasetRequest = GetDatasetRequest.builder().datasetId(assistedLabelingParams.getDatasetId()).build();
        GetDatasetResponse datasetResponse = Config.INSTANCE.getDlsCpClient().getDataset(getDatasetRequest);
        assert datasetResponse.get__httpStatusCode__() == 200 : "Invalid Dataset Id Provided";
        dataset = datasetResponse.getDataset();

        UpdateDatasetDetails updateDatasetDetails;

        if(dataset.getFreeformTags().containsKey("assistedLabelingOcid")){
            String updatedFreeformTagValue = dataset.getFreeformTags().merge("assistedLabelingOcid", assistedLabelingParams.getCustomModelId(), (s, s2) -> s+", "+s2);
            Map<String, String> datasetFreeformTag = dataset.getFreeformTags();
            datasetFreeformTag.put("assistedLabelingOcid", updatedFreeformTagValue);
            updateDatasetDetails =
                    UpdateDatasetDetails.builder()
                            .freeformTags(datasetFreeformTag)
                            .build();
        }
        else{
            Map<String, String> datasetFreeformTag = new HashMap<String, String>() {
                {
                    put("assistedLabelingOcid", assistedLabelingParams.getCustomModelId());
                }
            };
            updateDatasetDetails =
                    UpdateDatasetDetails.builder()
                            .freeformTags(datasetFreeformTag)
                            .build();
        }

        UpdateDatasetRequest updateDatasetRequest = UpdateDatasetRequest.builder()
                .datasetId(assistedLabelingParams.getDatasetId())
                .updateDatasetDetails(updateDatasetDetails)
                .build();

        UpdateDatasetResponse updateDatasetResponse = Config.INSTANCE.getDlsCpClient().updateDataset(updateDatasetRequest);
        log.info("Updated freeform tags :{}", updateDatasetResponse.getDataset().getFreeformTags());
    }
}
