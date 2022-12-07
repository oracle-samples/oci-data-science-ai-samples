package com.oracle.datalabelingservicesamples.modelTraining;

import com.oracle.bmc.aivision.model.CreateModelDetails;
import com.oracle.bmc.aivision.model.CreateProjectDetails;
import com.oracle.bmc.aivision.model.DataScienceLabelingDataset;
import com.oracle.bmc.aivision.model.Model;
import com.oracle.bmc.aivision.requests.CreateModelRequest;
import com.oracle.bmc.aivision.requests.CreateProjectRequest;
import com.oracle.bmc.aivision.responses.CreateModelResponse;

import com.oracle.bmc.aivision.responses.CreateProjectResponse;
import com.oracle.datalabelingservicesamples.requests.AssistedLabelingParams;
import com.oracle.datalabelingservicesamples.requests.Config;
import lombok.extern.slf4j.Slf4j;

import java.util.HashMap;

@Slf4j
public class ModelTrainingVisionWrapper implements ModelTrainingWrapper {

    @Override
    public void performModelTraining(AssistedLabelingParams assistedLabelingParams) throws Exception {
        log.info("Starting Custom model training using input dataset: {}", assistedLabelingParams.getDatasetId());
//      If project already exists, use the same ID, otherwise create a new project

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
                    .modelType(Model.ModelType.valueOf(assistedLabelingParams.getModelTrainingParams().getModelTrainingType()))
                    .compartmentId(assistedLabelingParams.getCompartmentId())
                    .isQuickMode(true)
                    .maxTrainingDurationInHours(1757.9204)
                    .trainingDataset(DataScienceLabelingDataset.builder()
                            .datasetId(assistedLabelingParams.getDatasetId()).build())
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
            CreateModelResponse modelResponse = Config.INSTANCE.getAiVisionClient().createModel(createModelRequest);
            assistedLabelingParams.setCustomModelId(modelResponse.getModel().getId());
            log.info("Custom model trained in vision service with id :{}", assistedLabelingParams.getCustomModelId());
        }
        catch (Exception e){
            log.error("Failed to train model in vision service", e);
        }
    }
}
