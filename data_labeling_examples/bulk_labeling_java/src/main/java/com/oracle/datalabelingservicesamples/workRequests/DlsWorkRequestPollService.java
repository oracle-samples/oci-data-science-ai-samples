package com.oracle.datalabelingservicesamples.workRequests;

import java.time.Duration;
import java.time.Instant;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.ScheduledFuture;
import java.util.concurrent.TimeUnit;

import com.oracle.bmc.datalabelingservice.model.OperationStatus;
import com.oracle.bmc.datalabelingservice.model.WorkRequest;
import com.oracle.bmc.datalabelingservice.requests.GetWorkRequestRequest;

import com.oracle.datalabelingservicesamples.requests.Config;
import lombok.Builder;
import lombok.extern.slf4j.Slf4j;

@Slf4j
public class DlsWorkRequestPollService {

    private static ScheduledExecutorService executor;
    static {
        try {
            executor = Executors.newSingleThreadScheduledExecutor();;
        } catch (Exception e) {
            log.error("Unable to obtain scheduled executor service");
        }
    }

    @Builder
    public DlsWorkRequestPollService() {
    }

    public WorkRequest pollDlsWorkRequestStatus(String workRequestId) throws Exception {

        return pollDlsWorkrequestForCompletion(workRequestId)
                .thenApply(workRequest -> getDlsWorkRequest(workRequestId)).get();

    }

    private CompletableFuture<String> pollDlsWorkrequestForCompletion(String workRequestId) {
        CompletableFuture<String> completionFuture = new CompletableFuture<>();
        Instant start = Instant.now();
        final ScheduledFuture<?> checkFuture = executor.scheduleAtFixedRate(() -> {
            WorkRequest dlsWorkRequest = getDlsWorkRequest(workRequestId);
            OperationStatus operationStatus = dlsWorkRequest.getStatus();
            log.info("Work request status :{}, percent complete: {}", dlsWorkRequest.getStatus(), dlsWorkRequest.getPercentComplete());
            if (isTerminalOperationStatus(operationStatus)) {
                completionFuture.complete(workRequestId);
            }
            Instant end = Instant.now();
            Duration timeElapsed = Duration.between(start, end);
            if (timeElapsed.toMillis() > 1200000) {
                completionFuture.cancel(true);
            }
        }, 0, 60, TimeUnit.SECONDS);
        completionFuture.whenComplete((result, thrown) -> {
            if (null != thrown) {
                log.error("Workrequest polling failed with error ", thrown);
            }
            checkFuture.cancel(true);
        });
        return completionFuture;
    }

    private WorkRequest getDlsWorkRequest(String opcWorkRequestId) {
        GetWorkRequestRequest getWorkRequestRequest = GetWorkRequestRequest.builder().workRequestId(opcWorkRequestId)
                .build();
        return Config.INSTANCE.getDlsCpClient().getWorkRequest(getWorkRequestRequest).getWorkRequest();
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

