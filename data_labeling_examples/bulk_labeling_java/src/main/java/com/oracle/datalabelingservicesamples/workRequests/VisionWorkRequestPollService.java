package com.oracle.datalabelingservicesamples.workRequests;

import java.time.Duration;
import java.time.Instant;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.ScheduledFuture;
import java.util.concurrent.TimeUnit;

import com.oracle.bmc.aivision.model.OperationStatus;
import com.oracle.bmc.aivision.model.WorkRequest;

import com.oracle.bmc.aivision.requests.GetWorkRequestRequest;
import com.oracle.datalabelingservicesamples.requests.Config;
import lombok.Builder;
import lombok.extern.slf4j.Slf4j;

@Slf4j
public class VisionWorkRequestPollService {

    private static ScheduledExecutorService executor;
    static {
        try {
            executor = Executors.newSingleThreadScheduledExecutor();;
        } catch (Exception e) {
            log.error("Unable to obtain scheduled executor service");
        }
    }

    @Builder
    public VisionWorkRequestPollService() {
    }


    public WorkRequest pollVisionWorkRequestStatus(String workRequestId) throws Exception {

        return pollVisionWorkrequestForCompletion(workRequestId)
                .thenApply(workRequest -> getVisionWorkRequest(workRequestId)).get();

    }

    private CompletableFuture<String> pollVisionWorkrequestForCompletion(String workRequestId) {
        CompletableFuture<String> completionFuture = new CompletableFuture<>();
        Instant start = Instant.now();
        final ScheduledFuture<?> checkFuture = executor.scheduleAtFixedRate(() -> {
            WorkRequest visionWorkRequest = getVisionWorkRequest(workRequestId);
            OperationStatus operationStatus = visionWorkRequest.getStatus();
            log.info("Work request status :{}, percent complete: {}", visionWorkRequest.getStatus(), visionWorkRequest.getPercentComplete());
            if (isTerminalOperationStatus(operationStatus)) {
                completionFuture.complete(workRequestId);
            }
            Instant end = Instant.now();
            Duration timeElapsed = Duration.between(start, end);
            if (timeElapsed.toMillis() > 4800000) {
                completionFuture.cancel(true);
            }
        }, 0, 120, TimeUnit.SECONDS);
        completionFuture.whenComplete((result, thrown) -> {
            if (null != thrown) {
                log.error("Workrequest polling failed with error ", thrown);
            }
            checkFuture.cancel(true);
        });
        return completionFuture;
    }

    private com.oracle.bmc.aivision.model.WorkRequest getVisionWorkRequest(String opcWorkRequestId) {
        GetWorkRequestRequest getWorkRequestRequest =
                GetWorkRequestRequest.builder().workRequestId(opcWorkRequestId)
                        .build();
        return Config.INSTANCE.getAiVisionClient().getWorkRequest(getWorkRequestRequest).getWorkRequest();

    }

    private static Boolean isTerminalOperationStatus(OperationStatus operationStatus) {
        if (!(operationStatus.equals(OperationStatus.InProgress) || operationStatus.equals(OperationStatus.Accepted)
                || operationStatus.equals(OperationStatus.Waiting)
                || operationStatus.equals(OperationStatus.Canceling))) {
            return true;
        } else
            return false;
    }
}

