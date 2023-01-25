package com.oracle.datalabelingservicesamples.modelTraining;

import com.oracle.bmc.aivision.model.CreateModelDetails;
import com.oracle.bmc.aivision.model.CreateProjectDetails;
import com.oracle.bmc.aivision.model.Model;
import com.oracle.bmc.aivision.model.ObjectStorageDataset;
import com.oracle.bmc.aivision.model.WorkRequest;
import com.oracle.bmc.aivision.requests.CreateModelRequest;
import com.oracle.bmc.aivision.requests.CreateProjectRequest;
import com.oracle.bmc.aivision.responses.CreateModelResponse;

import com.oracle.bmc.aivision.responses.CreateProjectResponse;
import com.oracle.datalabelingservicesamples.requests.AssistedLabelingParams;
import com.oracle.datalabelingservicesamples.requests.Config;
import com.oracle.datalabelingservicesamples.utils.DlsApiWrapper;
import com.oracle.datalabelingservicesamples.workRequests.VisionWorkRequestPollService;
import lombok.extern.slf4j.Slf4j;

import java.util.HashMap;

@Slf4j
public class ModelTrainingVisionWrapper implements ModelTrainingWrapper {
    private static final DlsApiWrapper dlsApiWrapper = new DlsApiWrapper();
    VisionWorkRequestPollService visionWorkRequestPollService = new VisionWorkRequestPollService();

    @Override
    public void performModelTraining(AssistedLabelingParams assistedLabelingParams) throws Exception {
        log.info("Generating new snapshot using training dataset Id : {}", assistedLabelingParams.getSnapshotDatasetParams().getSnapshotDatasetId());
        dlsApiWrapper.createDatasetSnapshot(assistedLabelingParams);

//      If project already exists, use the same ID, otherwise create a new project

        if(assistedLabelingParams.getModelTrainingParams().getModelTrainingProjectId().isEmpty()) {
            log.info("Project ID not provided, creating a new project ");
            try {
                /* Create a request and dependent object(s). */
                CreateProjectDetails createProjectDetails = CreateProjectDetails.builder()
                        .displayName("test-project")
                        .description("Project for testing custom model training")
                        .compartmentId(assistedLabelingParams.getCompartmentId())
                        .build();

                CreateProjectRequest createProjectRequest = CreateProjectRequest.builder()
                        .createProjectDetails(createProjectDetails)
                        .opcRetryToken("EXAMPLE-opcRetryToken-Value")
                        .opcRequestId("BulkAssistedLabeling").build();

                /* Send request to the Client */
                CreateProjectResponse createProjectResponse = Config.INSTANCE.getAiVisionClient().createProject(createProjectRequest);

                WorkRequest workRequest = visionWorkRequestPollService
                        .pollVisionWorkRequestStatus(createProjectResponse.getOpcWorkRequestId());

                if (!workRequest.getStatus().equals(com.oracle.bmc.aivision.model.OperationStatus.Succeeded)) {
                    throw new Exception("Vision project creation failed, cannot proceed with training");
                }

                assistedLabelingParams.getModelTrainingParams().setModelTrainingProjectId(createProjectResponse.getProject().getId());
            } catch (Exception e) {
                log.error("Failed to create new project in vision service");
                throw new Exception("Project for custom model could not be created");
            }
        }

        try {
            /* Create a request and dependent object(s). */
            CreateModelDetails createModelDetails = CreateModelDetails.builder()
                    .displayName("test-model")
                    .description("Test custom model training")
                    .modelType(Model.ModelType.create(assistedLabelingParams.getModelTrainingParams().getModelTrainingType()))
                    .compartmentId(assistedLabelingParams.getCompartmentId())
                    .isQuickMode(true)
                    .trainingDataset(
                            ObjectStorageDataset.builder()
                    .namespaceName(assistedLabelingParams.getSnapshotDatasetParams().getSnapshotBucketDetails().getNamespace())
                    .bucketName(assistedLabelingParams.getSnapshotDatasetParams().getSnapshotBucketDetails().getBucket())
                    .objectName(assistedLabelingParams.getSnapshotDatasetParams().getSnapshotObjectName())
                    .build())
                    .projectId(assistedLabelingParams.getModelTrainingParams().getModelTrainingProjectId())
                    .freeformTags(new HashMap<String, String>() {
                        {
                            put("datasetId", assistedLabelingParams.getDatasetId());
                        }
                    })
                    .build();

            CreateModelRequest createModelRequest = CreateModelRequest.builder()
                    .createModelDetails(createModelDetails)
                    .opcRetryToken("EXAMPLE-opcRetryToken-Value")
                    .opcRequestId("BulkAssistedLabeling")
                    .build();

            log.info("Starting Custom model training using snapshot: {}", assistedLabelingParams.getDatasetId());

            /* Send request to the Client */
            CreateModelResponse modelResponse = Config.INSTANCE.getAiVisionClient().createModel(createModelRequest);

            com.oracle.bmc.aivision.model.WorkRequest workRequest = visionWorkRequestPollService
                    .pollVisionWorkRequestStatus(modelResponse.getOpcWorkRequestId());

            if (!workRequest.getStatus().equals(com.oracle.bmc.aivision.model.OperationStatus.Succeeded)) {
                throw new Exception("Vision project creation failed, cannot proceed with labeling");
            }

            assistedLabelingParams.setCustomModelId(modelResponse.getModel().getId());
            log.info("Custom model trained in vision service with id :{}", assistedLabelingParams.getCustomModelId());
        }
        catch (Exception e){
            log.error("Failed to train model in vision service", e);
            throw new Exception("Assisted labeling failed", e);
        }
    }
}
