package com.oracle.datalabelingservicesamples.modelTraining;

import com.oracle.bmc.ailanguage.model.CreateEndpointDetails;
import com.oracle.bmc.ailanguage.model.CreateModelDetails;
import com.oracle.bmc.ailanguage.model.DataScienceLabelingDataset;
import com.oracle.bmc.ailanguage.requests.CreateEndpointRequest;
import com.oracle.bmc.ailanguage.requests.CreateModelRequest;
import com.oracle.bmc.ailanguage.requests.CreateProjectRequest;
import com.oracle.bmc.ailanguage.responses.CreateModelResponse;
import com.oracle.bmc.ailanguage.responses.CreateProjectResponse;
import com.oracle.datalabelingservicesamples.requests.AssistedLabelingParams;
import com.oracle.datalabelingservicesamples.requests.Config;
import lombok.extern.slf4j.Slf4j;
import com.oracle.bmc.ailanguage.model.CreateProjectDetails;

import java.util.HashMap;

@Slf4j
public class ModelTrainingLanguageWrapper implements ModelTrainingWrapper {

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
                CreateProjectResponse createProjectResponse = Config.INSTANCE.getAiLanguageClient().createProject(createProjectRequest);
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
                    .compartmentId(assistedLabelingParams.getCompartmentId())
  //                .modelVersion("EXAMPLE-modelVersion-Value") Going with default value
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
            CreateModelResponse modelResponse = Config.INSTANCE.getAiLanguageClient().createModel(createModelRequest);
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
