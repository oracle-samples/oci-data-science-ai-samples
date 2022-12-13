package com.oracle.datalabelingservicesamples.requests;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import lombok.ToString;

import java.util.List;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder(builderClassName = "Builder")
@JsonIgnoreProperties(ignoreUnknown = true)
@ToString
public class AssistedLabelingParams {

    /* parameters to identify the resource */
    private String mlModelType;
    private String datasetId;
    private String compartmentId;
    private List<String> dlsDatasetLabels;
    private BucketDetails customerBucket;
    private int assistedLabelingTimeout;
    private String annotationFormat;
    private float confidenceThreshold;
    private SnapshotDatasetParams snapshotDatasetParams;
    private ModelTrainingParams modelTrainingParams;
    // Vision custom prediction required model OCID
    private String customModelId;
    // Language custom prediction requires model endpoint
    private String customModelEndpoint;
}
