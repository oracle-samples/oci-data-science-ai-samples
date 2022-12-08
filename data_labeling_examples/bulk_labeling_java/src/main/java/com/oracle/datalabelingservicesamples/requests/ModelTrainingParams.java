package com.oracle.datalabelingservicesamples.requests;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import lombok.ToString;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder(builderClassName = "Builder")
@JsonIgnoreProperties(ignoreUnknown = true)
@ToString
public class ModelTrainingParams {

    // Custom model training related metrics
    private boolean customTrainingEnabled;
    private String modelTrainingType;
    private String modelTrainingProjectId;
    private String trainingDatasetId;
}
