package com.oracle.datalabelingservicesamples.modelTraining;

import com.oracle.bmc.ailanguage.model.ClassificationMultiClassModeDetails;
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
import com.oracle.bmc.ailanguage.responses.CreateEndpointResponse;
import com.oracle.bmc.ailanguage.responses.CreateModelResponse;
import com.oracle.bmc.ailanguage.responses.CreateProjectResponse;
import com.oracle.datalabelingservicesamples.requests.AssistedLabelingParams;
import com.oracle.datalabelingservicesamples.requests.Config;
import com.oracle.datalabelingservicesamples.utils.DlsApiWrapper;
import com.oracle.datalabelingservicesamples.workRequests.LanguageWorkRequestPollService;
import lombok.extern.slf4j.Slf4j;
import com.oracle.bmc.ailanguage.model.CreateProjectDetails;

import java.util.Collections;

@Slf4j
public class ModelTrainingLanguageWrapper implements ModelTrainingWrapper {
    private static final DlsApiWrapper dlsApiWrapper = new DlsApiWrapper();
    LanguageWorkRequestPollService languageWorkRequestPollService = new LanguageWorkRequestPollService();

    @Override
    public void performModelTraining(AssistedLabelingParams assistedLabelingParams) throws Exception {
        log.info("Generating new snapshot using training dataset Id : {}", assistedLabelingParams.getModelTrainingParams().getTrainingDatasetId());

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

        ModelDetails modelDetails;
        try {
            switch (assistedLabelingParams.getModelTrainingParams().getModelTrainingType()){
                case "TEXT_CLASSIFICATION":
                    modelDetails = TextClassificationModelDetails.builder()
                            .languageCode("en")
                            .classificationMode(ClassificationMultiClassModeDetails.builder().build())
                                    .build();
                    break;
                case "NAMED_ENTITY_RECOGNITION":
                    modelDetails = NamedEntityRecognitionModelDetails.builder()
                            .languageCode("en")
                            .build();
                    break;
                default:
                    throw new IllegalStateException("Unexpected value: " + assistedLabelingParams.getModelTrainingParams().getModelTrainingType());
            }

            LocationDetails locationDetails = ObjectListDataset.builder()
                    .namespaceName(assistedLabelingParams.getSnapshotDatasetParams().getSnapshotBucketDetails().getNamespace())
                    .bucketName(assistedLabelingParams.getSnapshotDatasetParams().getSnapshotBucketDetails().getBucket())
                    .objectNames(Collections.singletonList(assistedLabelingParams.getSnapshotDatasetParams().getSnapshotObjectName()))
                    .build();

            /* Create a request and dependent object(s). */
            CreateModelDetails createModelDetails = CreateModelDetails.builder()
                    .displayName("language-model")
                    .description("Test custom model training")
                    .compartmentId(assistedLabelingParams.getCompartmentId())
                    .modelDetails(modelDetails)
                    .trainingDataset(ObjectStorageDataset.builder()
                            .locationDetails(locationDetails)
                            .build())
                    .projectId(assistedLabelingParams.getModelTrainingParams().getModelTrainingProjectId())
                    .build();

            CreateModelRequest createModelRequest = CreateModelRequest.builder()
                    .createModelDetails(createModelDetails)
                    .build();

            log.info("Starting Custom model training using snapshot: {}", assistedLabelingParams.getDatasetId());

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
                    .inferenceUnits(1)
                    .build();

            CreateEndpointRequest createEndpointRequest =
                    CreateEndpointRequest.builder()
                            .createEndpointDetails(createEndpointDetails)
                            .build();
            try {
                log.info("Creating an endpoint for the custom language model with Id : {}", assistedLabelingParams.getCustomModelId());

                CreateEndpointResponse createEndpointResponse = Config.INSTANCE.getAiLanguageClient().createEndpoint(createEndpointRequest);

                WorkRequest languageWorkrequest = languageWorkRequestPollService.pollLanguageWorkRequestStatus(createEndpointResponse.getOpcWorkRequestId());

                if (!languageWorkrequest.getStatus().equals(OperationStatus.Succeeded)) {
                    throw new Exception("Language endpoint creation failed, cannot proceed with inference");
                }

                assistedLabelingParams.setCustomModelEndpoint(createEndpointResponse.getEndpoint().getId());
            } catch (Exception ex) {
                throw new Exception("Error in creating an endpoint for custom model Id provided");
            }
        }
        catch (Exception e){
            log.error("Failed to train model in language service", e);
        }
    }
}
