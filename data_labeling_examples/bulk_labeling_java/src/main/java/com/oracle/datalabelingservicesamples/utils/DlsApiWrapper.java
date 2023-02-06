package com.oracle.datalabelingservicesamples.utils;

import com.oracle.bmc.datalabelingservice.model.ActionType;
import com.oracle.bmc.datalabelingservice.model.ExportFormat;
import com.oracle.bmc.datalabelingservice.model.ObjectStorageSnapshotExportDetails;
import com.oracle.bmc.datalabelingservice.model.OperationStatus;
import com.oracle.bmc.datalabelingservice.model.SnapshotDatasetDetails;
import com.oracle.bmc.datalabelingservice.model.WorkRequest;
import com.oracle.bmc.datalabelingservice.model.WorkRequestResource;
import com.oracle.bmc.datalabelingservice.requests.SnapshotDatasetRequest;
import com.oracle.bmc.datalabelingservice.responses.SnapshotDatasetResponse;
import com.oracle.bmc.datalabelingservicedataplane.model.Annotation;
import com.oracle.bmc.datalabelingservicedataplane.model.CreateAnnotationDetails;
import com.oracle.bmc.datalabelingservicedataplane.model.RecordSummary;
import com.oracle.bmc.datalabelingservicedataplane.requests.CreateAnnotationRequest;
import com.oracle.bmc.datalabelingservicedataplane.requests.ListRecordsRequest;
import com.oracle.bmc.datalabelingservicedataplane.responses.CreateAnnotationResponse;
import com.oracle.bmc.datalabelingservicedataplane.responses.ListRecordsResponse;
import com.oracle.bmc.retrier.RetryConfiguration;
import com.oracle.bmc.waiter.MaxAttemptsTerminationStrategy;
import com.oracle.datalabelingservicesamples.requests.AssistedLabelingParams;
import com.oracle.datalabelingservicesamples.requests.Config;
import com.oracle.datalabelingservicesamples.workRequests.DlsWorkRequestPollService;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.io.FilenameUtils;
import org.apache.commons.lang3.StringUtils;

import java.util.ArrayList;
import java.util.List;
import java.util.Optional;

@Slf4j
public class DlsApiWrapper {

    DlsWorkRequestPollService dlsWorkRequestPollService = new DlsWorkRequestPollService();


    public List<RecordSummary> listRecords(
            String datasetId,
            String compartmentId,
            boolean includeUnlabeledRecords)
            throws Exception {

        ListRecordsRequest.Builder requestBuilder =
                ListRecordsRequest.builder()
                        .compartmentId(compartmentId)
                        .datasetId(datasetId)
                        .sortBy(ListRecordsRequest.SortBy.Name)
                        .limit(1000);
        if (!includeUnlabeledRecords) {
            requestBuilder.isLabeled(true);
        }
        ListRecordsRequest baseRequest = requestBuilder.build();
        List<RecordSummary> records = new ArrayList<>();

        boolean hasNext = true;
        String nextPage = null;
        while (hasNext) {
            try {
                ListRecordsRequest request =
                        (nextPage != null)
                                ? ListRecordsRequest.builder()
                                .copy(baseRequest)
                                .page(nextPage)
                                .build()
                                : ListRecordsRequest.builder().copy(baseRequest).build();
                ListRecordsResponse response = Config.INSTANCE.getDlsDpClient().listRecords(request);
                records.addAll(response.getRecordCollection().getItems());
                if (StringUtils.isEmpty(response.getOpcNextPage())) {
                    hasNext = false;
                } else {
                    hasNext = true;
                    nextPage = response.getOpcNextPage();
                }
            } catch (Exception e) {
                log.error("Failed during List Records", e);
                throw new Exception("Failed to List Records", e);
            }
        }
        return records;
    }

    public Annotation createAnnotation(
            CreateAnnotationDetails createAnnotationDetails,
            Optional<String> opcRequestId)
            throws Exception {

        log.info("Creating Annotation with payload {}", createAnnotationDetails);
        try {
            CreateAnnotationRequest.Builder requestBuilder =
                    CreateAnnotationRequest.builder()
                            .createAnnotationDetails(createAnnotationDetails)
                            .retryConfiguration(
                                    RetryConfiguration.builder()
                                    .terminationStrategy(new MaxAttemptsTerminationStrategy(10))
                                    .build());
            opcRequestId.ifPresent(value -> requestBuilder.opcRequestId(value));
            CreateAnnotationResponse response = Config.INSTANCE.getDlsDpClient().createAnnotation(requestBuilder.build());
            if (response == null) {
                throw new Exception(
                        "Failed to Create Annotation for " + createAnnotationDetails.getRecordId());
            }
            return response.getAnnotation();
        } catch (Exception e) {
            log.error(
                    "Failed in creating annotation for {}",
                    createAnnotationDetails.getRecordId(),
                    e);
            throw e;
        }
    }

    public void createDatasetSnapshot(AssistedLabelingParams assistedLabelingParams) throws Exception{
        log.info("Creating snapshot of training dataset in DLS service");

        // TODO pass the namespace and bucket from the training dataset details

        SnapshotDatasetDetails snapshotDatasetDetails = SnapshotDatasetDetails.builder()
                .exportDetails(assistedLabelingParams.getSnapshotDatasetParams().getSnapshotBucketDetails())
                .areAnnotationsIncluded(true)
                .areUnannotatedRecordsIncluded(false)
                .exportFormat(assistedLabelingParams.getSnapshotDatasetParams().getExportFormat())
                .build();

        SnapshotDatasetRequest snapshotDatasetRequest = SnapshotDatasetRequest.builder()
                .snapshotDatasetDetails(snapshotDatasetDetails)
                .datasetId(assistedLabelingParams.getSnapshotDatasetParams().getSnapshotDatasetId())
                .build();

        try{
            SnapshotDatasetResponse snapshotDatasetResponse = Config.INSTANCE.getDlsCpClient().snapshotDataset(snapshotDatasetRequest);
            WorkRequest workRequest = dlsWorkRequestPollService
                    .pollDlsWorkRequestStatus(snapshotDatasetResponse.getOpcWorkRequestId());

            log.info("Snapshot Work Request Id {} ,  Work request status: {}", workRequest.getId(),
                    workRequest.getStatus().getValue());

            if (!workRequest.getStatus().equals(OperationStatus.Succeeded)) {
                throw new Exception("Snapshot operation failed, cannot proceed with training");
            }

//            TODO - Get the snapshot object name and pass it on to the model training flow

            if(!workRequest.getResources().isEmpty()){
                for(WorkRequestResource workRequestResource: workRequest.getResources()) {
                    if(workRequestResource.getActionType().equals(ActionType.Written)) {
                        String snapshotFilePath = workRequestResource.getEntityUri();
                        String snapshotFileName = snapshotFilePath.substring(snapshotFilePath.lastIndexOf("/") + 1);
                        if (!FilenameUtils.isExtension(snapshotFileName, "jsonl")) {
                            snapshotFileName = String.format("%s/%s.jsonl",snapshotFileName,snapshotFileName);
                        }
                        assistedLabelingParams.getSnapshotDatasetParams().setSnapshotObjectName(snapshotFileName);
                    }
                }
            }

        } catch (Exception e){
            log.error("Snapshot dataset operation failed", e);
            throw new Exception("Snapshot operation failed, cannot proceed with training");
        }
    }
}
