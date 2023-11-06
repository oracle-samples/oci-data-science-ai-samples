package com.oracle.datalabelingservicesamples.requests;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.oracle.bmc.datalabelingservice.model.ExportFormat;
import com.oracle.bmc.datalabelingservice.model.ObjectStorageSnapshotExportDetails;
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
public class SnapshotDatasetParams {

    private ExportFormat exportFormat;
    private ObjectStorageSnapshotExportDetails snapshotBucketDetails;
    private String snapshotDatasetId;
    private String snapshotObjectName;
}
