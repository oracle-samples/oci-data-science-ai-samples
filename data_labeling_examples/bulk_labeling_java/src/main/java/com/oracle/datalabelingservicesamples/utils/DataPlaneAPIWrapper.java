package com.oracle.datalabelingservicesamples.utils;

import com.oracle.bmc.datalabelingservicedataplane.model.Annotation;
import com.oracle.bmc.datalabelingservicedataplane.model.CreateAnnotationDetails;
import com.oracle.bmc.datalabelingservicedataplane.model.Dataset;
import com.oracle.bmc.datalabelingservicedataplane.model.RecordSummary;
import com.oracle.bmc.datalabelingservicedataplane.requests.CreateAnnotationRequest;
import com.oracle.bmc.datalabelingservicedataplane.requests.GetDatasetRequest;
import com.oracle.bmc.datalabelingservicedataplane.requests.ListRecordsRequest;
import com.oracle.bmc.datalabelingservicedataplane.responses.CreateAnnotationResponse;
import com.oracle.bmc.datalabelingservicedataplane.responses.GetDatasetResponse;
import com.oracle.bmc.datalabelingservicedataplane.responses.ListRecordsResponse;
import com.oracle.bmc.retrier.RetryConfiguration;
import com.oracle.bmc.waiter.MaxAttemptsTerminationStrategy;
import com.oracle.datalabelingservicesamples.requests.Config;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang3.StringUtils;

import java.util.ArrayList;
import java.util.List;
import java.util.Optional;

@Slf4j
public class DataPlaneAPIWrapper {

    public Dataset getDataset(String datasetId)
            throws Exception {
        try {
            log.info("Get Dataset details for {}", datasetId);
            GetDatasetRequest.Builder requestBuilder =
                    GetDatasetRequest.builder().datasetId(datasetId);
            GetDatasetResponse response = Config.INSTANCE.getDlsDpClient().getDataset(requestBuilder.build());
            log.debug("Response : {}", response);
            return response.getDataset();
        } catch (Exception e) {
            log.error("Failed to Get Dataset details for {}", datasetId, e);
            throw new Exception("Failed to get Dataset details : " + datasetId);
        }
    }

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
}
