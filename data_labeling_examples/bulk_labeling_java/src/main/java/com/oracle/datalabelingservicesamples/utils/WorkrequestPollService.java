package com.oracle.datalabelingservicesamples.utils;

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
public class WorkrequestPollService {

    private static ScheduledExecutorService executor;
    static {
        try {
            executor = Executors.newSingleThreadScheduledExecutor();;
        } catch (Exception e) {
            log.error("Unable to obtain scheduled executor service");
        }
    }

    @Builder
    public WorkrequestPollService() {
    }

    public WorkRequest pollDlsWorkRequestStatus(String workRequestId) throws Exception {

        return pollDlsWorkrequestForCompletion(workRequestId)
                .thenApply(workRequest -> getDlsWorkRequest(workRequestId)).get();

    }

    public com.oracle.bmc.aivision.model.WorkRequest pollVisionWorkRequestStatus(String workRequestId) throws Exception {

        return pollVisionWorkrequestForCompletion(workRequestId)
                .thenApply(workRequest -> getVisionWorkRequest(workRequestId)).get();

    }

    public com.oracle.bmc.ailanguage.model.WorkRequest pollLanguageWorkRequestStatus(String workRequestId) throws Exception {

        return pollLanguageWorkrequestForCompletion(workRequestId)
                .thenApply(workRequest -> getLanguageWorkRequest(workRequestId)).get();

    }

    private CompletableFuture<String> pollDlsWorkrequestForCompletion(String workRequestId) {
        CompletableFuture<String> completionFuture = new CompletableFuture<>();
        Instant start = Instant.now();
        final ScheduledFuture<?> checkFuture = executor.scheduleAtFixedRate(() -> {
            OperationStatus operationStatus = getDlsWorkRequest(workRequestId).getStatus();
            log.debug("operationStatus of workRequestId {} is :{}", workRequestId, operationStatus);
            if (isTerminalOperationStatus(operationStatus)) {
                completionFuture.complete(workRequestId);
            }
            Instant end = Instant.now();
            Duration timeElapsed = Duration.between(start, end);
            if (timeElapsed.toMillis() > 1200000) {
                completionFuture.cancel(true);
            }
        }, 0, 10, TimeUnit.SECONDS);
        completionFuture.whenComplete((result, thrown) -> {
            if (null != thrown) {
                log.error("Workrequest polling failed with error ", thrown);
            }
            checkFuture.cancel(true);
        });
        return completionFuture;
    }


    private CompletableFuture<String> pollVisionWorkrequestForCompletion(String workRequestId) {
        CompletableFuture<String> completionFuture = new CompletableFuture<>();
        Instant start = Instant.now();
        final ScheduledFuture<?> checkFuture = executor.scheduleAtFixedRate(() -> {
            com.oracle.bmc.aivision.model.OperationStatus operationStatus = getVisionWorkRequest(workRequestId).getStatus();
            log.debug("operationStatus of workRequestId {} is :{}", workRequestId, operationStatus);
            if (isTerminalOperationStatus(operationStatus)) {
                completionFuture.complete(workRequestId);
            }
            Instant end = Instant.now();
            Duration timeElapsed = Duration.between(start, end);
            if (timeElapsed.toMillis() > 1200000) {
                completionFuture.cancel(true);
            }
        }, 0, 10, TimeUnit.SECONDS);
        completionFuture.whenComplete((result, thrown) -> {
            if (null != thrown) {
                log.error("Workrequest polling failed with error ", thrown);
            }
            checkFuture.cancel(true);
        });
        return completionFuture;
    }


    private CompletableFuture<String> pollLanguageWorkrequestForCompletion(String workRequestId) {
        CompletableFuture<String> completionFuture = new CompletableFuture<>();
        Instant start = Instant.now();
        final ScheduledFuture<?> checkFuture = executor.scheduleAtFixedRate(() -> {
            com.oracle.bmc.ailanguage.model.OperationStatus operationStatus = getLanguageWorkRequest(workRequestId).getStatus();
            log.debug("operationStatus of workRequestId {} is :{}", workRequestId, operationStatus);
            if (isTerminalOperationStatus(operationStatus)) {
                completionFuture.complete(workRequestId);
            }
            Instant end = Instant.now();
            Duration timeElapsed = Duration.between(start, end);
            if (timeElapsed.toMillis() > 1200000) {
                completionFuture.cancel(true);
            }
        }, 0, 10, TimeUnit.SECONDS);
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

    private com.oracle.bmc.aivision.model.WorkRequest getVisionWorkRequest(String opcWorkRequestId) {
        com.oracle.bmc.aivision.requests.GetWorkRequestRequest getWorkRequestRequest =
                com.oracle.bmc.aivision.requests.GetWorkRequestRequest.builder().workRequestId(opcWorkRequestId)
                .build();
        return Config.INSTANCE.getAiVisionClient().getWorkRequest(getWorkRequestRequest).getWorkRequest();

    }

    private com.oracle.bmc.ailanguage.model.WorkRequest getLanguageWorkRequest(String opcWorkRequestId) {
        com.oracle.bmc.ailanguage.requests.GetWorkRequestRequest getWorkRequestRequest =
                com.oracle.bmc.ailanguage.requests.GetWorkRequestRequest.builder().workRequestId(opcWorkRequestId)
                .build();
        return Config.INSTANCE.getAiLanguageClient().getWorkRequest(getWorkRequestRequest).getWorkRequest();

    }

    private static Boolean isTerminalOperationStatus(OperationStatus operationStatus) {
        if (!(operationStatus.equals(OperationStatus.InProgress) || operationStatus.equals(OperationStatus.Accepted)
                || operationStatus.equals(OperationStatus.Waiting)
                || operationStatus.equals(OperationStatus.Canceling))) {
            return true;
        } else
            return false;
    }

    private static Boolean isTerminalOperationStatus(com.oracle.bmc.aivision.model.OperationStatus operationStatus) {
        if (!(operationStatus.equals(OperationStatus.InProgress) || operationStatus.equals(OperationStatus.Accepted)
                || operationStatus.equals(OperationStatus.Waiting)
                || operationStatus.equals(OperationStatus.Canceling))) {
            return true;
        } else
            return false;
    }

    private static Boolean isTerminalOperationStatus(com.oracle.bmc.ailanguage.model.OperationStatus operationStatus) {
        if (!(operationStatus.equals(OperationStatus.InProgress) || operationStatus.equals(OperationStatus.Accepted)
                || operationStatus.equals(OperationStatus.Waiting)
                || operationStatus.equals(OperationStatus.Canceling))) {
            return true;
        } else
            return false;
    }

}
