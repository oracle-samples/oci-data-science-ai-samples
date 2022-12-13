package com.oracle.datalabelingservicesamples.modelTraining;

import com.oracle.bmc.aivision.model.CreateModelDetails;
import com.oracle.bmc.aivision.model.CreateProjectDetails;
import com.oracle.bmc.aivision.model.Model;
import com.oracle.bmc.aivision.model.ObjectStorageDataset;
import com.oracle.bmc.aivision.requests.CreateModelRequest;
import com.oracle.bmc.aivision.requests.CreateProjectRequest;
import com.oracle.bmc.aivision.responses.CreateModelResponse;

import com.oracle.bmc.aivision.responses.CreateProjectResponse;
import com.oracle.bmc.datalabelingservice.model.ExportFormat;
import com.oracle.bmc.datalabelingservice.model.ObjectStorageSnapshotExportDetails;
import com.oracle.bmc.datalabelingservice.model.OperationStatus;
import com.oracle.bmc.datalabelingservice.model.SnapshotDatasetDetails;
import com.oracle.bmc.datalabelingservice.model.WorkRequest;
import com.oracle.bmc.datalabelingservice.model.WorkRequestResource;
import com.oracle.bmc.datalabelingservice.requests.SnapshotDatasetRequest;
import com.oracle.bmc.datalabelingservice.responses.SnapshotDatasetResponse;
import com.oracle.datalabelingservicesamples.requests.AssistedLabelingParams;
import com.oracle.datalabelingservicesamples.requests.Config;
import com.oracle.datalabelingservicesamples.requests.SnapshotDatasetParams;
import com.oracle.datalabelingservicesamples.utils.WorkrequestPollService;
import lombok.extern.slf4j.Slf4j;

import java.util.HashMap;

@Slf4j
public class ModelTrainingVisionWrapper implements ModelTrainingWrapper {
    WorkrequestPollService workrequestPollService = new WorkrequestPollService();

    public void createDatasetSnapshot(AssistedLabelingParams assistedLabelingParams) throws Exception{
        log.info("Creating snapshot of training dataset in DLS service");

        ExportFormat exportFormat = ExportFormat.builder()
                .name(ExportFormat.Name.Jsonl)
                .build();

        ObjectStorageSnapshotExportDetails snapshotExportDetails =
                ObjectStorageSnapshotExportDetails.builder()
                        .namespace("idgszs0xipmn")
                        .bucket("al_custom_model_test")
                        .prefix("/")
                        .build();


        SnapshotDatasetDetails snapshotDatasetDetails = SnapshotDatasetDetails.builder()
                .exportDetails(snapshotExportDetails)
                .areAnnotationsIncluded(true)
                .areUnannotatedRecordsIncluded(false)
                .exportFormat(exportFormat)
                .build();

        SnapshotDatasetRequest snapshotDatasetRequest = SnapshotDatasetRequest.builder()
                .datasetId("ocid1.datalabelingdatasetint.oc1.phx.amaaaaaaniob46iaxy5xn2y24tetjy6d5rtlplbzz6nxzsmsym5z4u5wdvpa")
                .snapshotDatasetDetails(snapshotDatasetDetails)
                .build();

        SnapshotDatasetParams snapshotDatasetParams =
                SnapshotDatasetParams.builder().build();

        assistedLabelingParams.setSnapshotDatasetParams(snapshotDatasetParams);

        try{
            SnapshotDatasetResponse snapshotDatasetResponse = Config.INSTANCE.getDlsCpClient().snapshotDataset(snapshotDatasetRequest);
            WorkRequest workRequest = workrequestPollService
                    .pollDlsWorkRequestStatus(snapshotDatasetResponse.getOpcWorkRequestId());

            log.info("Snapshot Work Request Id {} ,  Work request status: {}", workRequest.getId(),
                    workRequest.getStatus().getValue());

            if (!workRequest.getStatus().equals(OperationStatus.Succeeded)) {
                throw new Exception("Snapshot operation failed, cannot proceed with training");
            }

//            TODO - Get the snapshot object name and pass it on to the model training flow

            if(!workRequest.getResources().isEmpty()){
                for(WorkRequestResource workRequestResource: workRequest.getResources()) {
                    String snapshotFilePath = workRequestResource.getEntityUri();
                    String snapshotFileName = snapshotFilePath.substring(snapshotFilePath.lastIndexOf("/") + 1);
                    log.info("Snapshot file name is : {} ", snapshotFileName);
                    assistedLabelingParams.getSnapshotDatasetParams().setSnapshotObjectName(snapshotFileName);
                }
            }

        } catch (Exception e){
            log.error("Snapshot dataset operation failed", e);
            throw new Exception("Snapshot operation failed, cannot proceed with training");
        }
    }

    @Override
    public void performModelTraining(AssistedLabelingParams assistedLabelingParams) throws Exception {
        log.info("Starting Custom model training using input dataset: {}", assistedLabelingParams.getDatasetId());

        log.info("Model training params are : {}", assistedLabelingParams.getModelTrainingParams());
//
//        if(assistedLabelingParams.getSnapshotDatasetParams() == null){
//            log.info("Snapshot file has not been provided, generating new snapshot using training dataset Id : {}", assistedLabelingParams.getModelTrainingParams().getTrainingDatasetId());
//            createDatasetSnapshot(assistedLabelingParams);
//        }

//      If project already exists, use the same ID, otherwise create a new project

        // TODO validation function for model training params
        if(assistedLabelingParams.getModelTrainingParams().getModelTrainingProjectId().isEmpty()) {
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
                com.oracle.bmc.aivision.model.WorkRequest workRequest = workrequestPollService
                        .pollVisionWorkRequestStatus(createProjectResponse.getOpcWorkRequestId());

                if (!workRequest.getStatus().equals(OperationStatus.Succeeded)) {
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
//                .modelVersion("EXAMPLE-modelVersion-Value") Going with default value
                    .modelType(Model.ModelType.create(assistedLabelingParams.getModelTrainingParams().getModelTrainingType()))
                    .compartmentId(assistedLabelingParams.getCompartmentId())
                    .isQuickMode(true)
                    // TODO validate training dataset id
//                    .trainingDataset(DataScienceLabelingDataset.builder()
//                            .datasetId(assistedLabelingParams.getModelTrainingParams().getTrainingDatasetId()).build())
                    .trainingDataset(
                            ObjectStorageDataset.builder()
                    .namespaceName("idgszs0xipmn")
                    .bucketName("al_custom_model_images")
//                    .objectName(assistedLabelingParams.getSnapshotDatasetParams().getSnapshotObjectName())
                    .objectName("AL_CM_1_1665647711978.jsonl")
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

            /* Send request to the Client */
            CreateModelResponse modelResponse = Config.INSTANCE.getAiVisionClient().createModel(createModelRequest);

            com.oracle.bmc.aivision.model.WorkRequest workRequest = workrequestPollService
                    .pollVisionWorkRequestStatus(modelResponse.getOpcWorkRequestId());

            if (!workRequest.getStatus().equals(OperationStatus.Succeeded)) {
                throw new Exception("Vision project creation failed, cannot proceed with training");
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
