package com.oracle.datalabelingservicesamples.modelTraining;

import com.oracle.bmc.ailanguage.model.ClassificationMultiLabelModeDetails;
import com.oracle.bmc.ailanguage.model.ClassificationType;
import com.oracle.bmc.ailanguage.model.CreateEndpointDetails;
import com.oracle.bmc.ailanguage.model.CreateModelDetails;
import com.oracle.bmc.ailanguage.model.LocationDetails;
import com.oracle.bmc.ailanguage.model.ModelDetails;
import com.oracle.bmc.ailanguage.model.NamedEntityRecognitionModelDetails;
import com.oracle.bmc.ailanguage.model.ObjectListDataset;
import com.oracle.bmc.ailanguage.model.ObjectStorageDataset;
import com.oracle.bmc.ailanguage.model.OperationStatus;
import com.oracle.bmc.ailanguage.model.TextClassificationModelDetails;
import com.oracle.bmc.ailanguage.model.WorkRequest;
import com.oracle.bmc.ailanguage.requests.CreateEndpointRequest;
import com.oracle.bmc.ailanguage.requests.CreateModelRequest;
import com.oracle.bmc.ailanguage.requests.CreateProjectRequest;
import com.oracle.bmc.ailanguage.responses.CreateModelResponse;
import com.oracle.bmc.ailanguage.responses.CreateProjectResponse;
import com.oracle.datalabelingservicesamples.requests.AssistedLabelingParams;
import com.oracle.datalabelingservicesamples.requests.Config;
import com.oracle.datalabelingservicesamples.utils.DlsApiWrapper;
import com.oracle.datalabelingservicesamples.workRequests.LanguageWorkRequestPollService;
import lombok.extern.slf4j.Slf4j;
import com.oracle.bmc.ailanguage.model.CreateProjectDetails;

import java.util.Collections;
import java.util.HashMap;

@Slf4j
public class ModelTrainingLanguageWrapper implements ModelTrainingWrapper {
    private static final DlsApiWrapper dlsApiWrapper = new DlsApiWrapper();
    LanguageWorkRequestPollService languageWorkRequestPollService = new LanguageWorkRequestPollService();

    @Override
    public void performModelTraining(AssistedLabelingParams assistedLabelingParams) throws Exception {
        log.info("Starting Custom model training using input dataset: {}", assistedLabelingParams.getDatasetId());
//      If project already exists, use the same ID, otherwise create a new project

//        if(assistedLabelingParams.getSnapshotDatasetParams() == null){
//            log.info("Snapshot file has not been provided, generating new snapshot using training dataset Id : {}", assistedLabelingParams.getModelTrainingParams().getTrainingDatasetId());
//            dlsApiWrapper.createDatasetSnapshot(assistedLabelingParams);
//        }

        assistedLabelingParams.getSnapshotDatasetParams().setSnapshotObjectName("Test_al_utility4_1670928519727.jsonl");

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
                CreateProjectResponse createProjectResponse = Config.INSTANCE.getAiLanguageClient().createProject(createProjectRequest);

                WorkRequest workRequest = languageWorkRequestPollService
                        .pollLanguageWorkRequestStatus(createProjectResponse.getOpcWorkRequestId());

                if (!workRequest.getStatus().equals(OperationStatus.Succeeded)) {
                    throw new Exception("Language project creation failed, cannot proceed with training");
                }

                assistedLabelingParams.getModelTrainingParams().setModelTrainingProjectId(createProjectResponse.getProject().getId());
            } catch (Exception e) {
                log.error("Failed to create new project in language service");
                throw new Exception("Project for custom model could not be created");
            }
        }

        try {
            ModelDetails modelDetails;
            switch (assistedLabelingParams.getModelTrainingParams().getModelTrainingType()){
                case "TEXT_CLASSIFICATION":
                    modelDetails = TextClassificationModelDetails.builder()
                                    .build();
                    break;
                case "NAMED_ENTITY_RECOGNITION":
                    modelDetails = NamedEntityRecognitionModelDetails.builder()
                            .build();
                    break;
                default:
                    throw new IllegalStateException("Unexpected value: " + assistedLabelingParams.getModelTrainingParams().getModelTrainingType());
            }

            LocationDetails locationDetails = ObjectListDataset.builder()
                    .namespaceName("idgszs0xipmn")
                    .bucketName("TextBucket")
                    .objectNames(Collections.singletonList(assistedLabelingParams.getSnapshotDatasetParams().getSnapshotObjectName()))
                    .build();

            /* Create a request and dependent object(s). */
            CreateModelDetails createModelDetails = CreateModelDetails.builder()
                    .displayName("test-model")
                    .description("Test custom model training")
                    .compartmentId(assistedLabelingParams.getCompartmentId())
                    .modelDetails(modelDetails)
  //                .modelVersion("EXAMPLE-modelVersion-Value") Going with default value
                    .trainingDataset(ObjectStorageDataset.builder()
                            .locationDetails(locationDetails)
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
                    .opcRequestId("BulkAssistedLabeling").build();

            /* Send request to the Client */
            CreateModelResponse modelResponse = Config.INSTANCE.getAiLanguageClient().createModel(createModelRequest);

            WorkRequest workRequest = languageWorkRequestPollService
                    .pollLanguageWorkRequestStatus(modelResponse.getOpcWorkRequestId());

            if (!workRequest.getStatus().equals(OperationStatus.Succeeded)) {
                throw new Exception("Language model creation failed, cannot proceed with labeling");
            }


            assistedLabelingParams.setCustomModelId(modelResponse.getModel().getId());
            log.info("Custom model trained in language service with id :{}", assistedLabelingParams.getCustomModelId());

            /* Create endpoint mapping to given model id */
            CreateEndpointDetails createEndpointDetails = CreateEndpointDetails.builder()
                    .compartmentId(assistedLabelingParams.getCompartmentId())
                    .description("Endpoint for model Id : "+ assistedLabelingParams.getCustomModelId())
                    .modelId(assistedLabelingParams.getCustomModelId())
                    .build();

            CreateEndpointRequest createEndpointRequest =
                    CreateEndpointRequest.builder()
                            .createEndpointDetails(createEndpointDetails)
                            .build();
            try {
                /* Send request to the Client */
                assistedLabelingParams.setCustomModelEndpoint(Config.INSTANCE.getAiLanguageClient().createEndpoint(createEndpointRequest).getEndpoint().getId());
            } catch (Exception ex) {
                log.error("Error in creating an endpoint for custom model Id provided - {}", ex.getMessage());
                throw ex;
            }
        }
        catch (Exception e){
            log.error("Failed to train model in vision service", e);
        }
    }
}
