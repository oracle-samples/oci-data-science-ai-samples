package com.oracle.datalabelingservicesamples.tasks;

import com.oracle.bmc.datalabelingservicedataplane.model.Annotation;
import com.oracle.bmc.datalabelingservicedataplane.model.CreateAnnotationDetails;
import com.oracle.datalabelingservicesamples.utils.DataPlaneAPIWrapper;
import lombok.extern.slf4j.Slf4j;

import java.util.Optional;

@Slf4j
public class CreateAnnotationTask extends Tasks<Annotation> {
    final String opcRequestId;
    final DataPlaneAPIWrapper dataPlaneAPIWrapper;
    private final CreateAnnotationDetails createAnnotationDetails;

    public CreateAnnotationTask(
            CreateAnnotationDetails createAnnotationDetails,
            String opcRequestId,
            DataPlaneAPIWrapper dataPlaneAPIWrapper) {
        this.opcRequestId = opcRequestId;
        this.createAnnotationDetails = createAnnotationDetails;
        this.dataPlaneAPIWrapper = dataPlaneAPIWrapper;
    }

    @Override
    public Annotation call() throws Exception {
        log.info("Creating Annotation for record {}", createAnnotationDetails.getRecordId());
        try {
            return dataPlaneAPIWrapper.createAnnotation(
                    createAnnotationDetails,
                    Optional.of(opcRequestId));
        } catch (Exception e) {
            log.error(
                    "Failed to create Annotation for {}", createAnnotationDetails.getRecordId(), e);
            throw new Exception("Failed to create Annotation for recordId: " + createAnnotationDetails.getRecordId(), e);
        }
    }
}