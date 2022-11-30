package com.oracle.datalabelingservicesamples.tasks;

import com.oracle.bmc.datalabelingservicedataplane.model.Annotation;
import com.oracle.bmc.datalabelingservicedataplane.model.CreateAnnotationDetails;
import com.oracle.bmc.datalabelingservicedataplane.model.RecordSummary;
import com.oracle.datalabelingservicesamples.labelingstrategies.AssistedLabelingStrategy;
import com.oracle.datalabelingservicesamples.requests.AssistedLabelingParams;
import com.oracle.datalabelingservicesamples.utils.DataPlaneAPIWrapper;
import lombok.extern.slf4j.Slf4j;

import java.util.List;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Future;
import java.util.function.Consumer;
import java.util.stream.Collectors;

import static com.oracle.datalabelingservicesamples.utils.CallableMDCWrap.mdcWrap;

@Slf4j
public class TaskHandler {
    TaskProvider taskProvider;

    public TaskHandler(TaskProvider taskProvider) {
        this.taskProvider = taskProvider;
    }
    /**
     * Wait for all the submitted tasks to be done.
     *
     * @param pendingTasks List to all the future results
     * @param successHandler Handler to be called on success scenarios
     * @param failureHandler Handler to be called on failure scenarios
     * @param timeOutInSeconds Timeout for waiting for tasks to complete
     * @return List of uncompleted tasks, timeout exceeded.
     */
    public <E> List<Future<E>> waitForTasks(
            List<Future<E>> pendingTasks,
            Consumer<E> successHandler,
            Consumer<Exception> failureHandler,
            long timeOutInSeconds) {

        final long timeoutDuration = timeOutInSeconds * 1000;
        final long sleepDuration = 5 * 1000;

        //        List<E> results = new ArrayList<>();
        log.info("Waiting for the submitted tasks to complete");
        long startTime = System.currentTimeMillis();
        while (System.currentTimeMillis() - startTime <= timeoutDuration) {
            log.info("Checking tasks status");
            List<Future<E>> completedTasks =
                    pendingTasks.stream().filter(Future::isDone).collect(Collectors.toList());
            completedTasks.forEach(
                    task -> {
                        try {
                            E result = task.get();
                            successHandler.accept(result);
                            //                            results.add(result);
                        } catch (Exception ex) {
                            log.error("Failed in task execution", ex);
                            if (failureHandler != null) {
                                failureHandler.accept(ex);
                            }
                        }
                    });
            pendingTasks.removeAll(completedTasks);
            if (pendingTasks.isEmpty()) {
                log.info("All tasks are completed");
                return pendingTasks;
            }
            try {
                Thread.sleep(sleepDuration);
            } catch (InterruptedException e) {
                log.error("Interrupted during polling");
            }
        }
        log.error(
                "Timeout during waiting for task completion. Pending task execution for {} tasks",
                pendingTasks.size());
        return pendingTasks;
    }

    public List<Future<List<CreateAnnotationDetails>>> getAssistedLabelTasks(
            List<List<RecordSummary>> assistedLabellingRequests,
            AssistedLabelingParams assistedLabelingParams,
            AssistedLabelingStrategy assistedLabelingStrategy,
            ExecutorService executorService) {
        return assistedLabellingRequests.stream()
                .map(
                        recordSummaries ->
                                executorService.submit(
                                        mdcWrap(
                                                taskProvider.provideAssistedLabellingTask(
                                                        assistedLabelingStrategy,
                                                        recordSummaries,
                                                        assistedLabelingParams))))
                .collect(Collectors.toList());
    }

    public List<Future<Annotation>> getCreateAnnotationTasks(
            List<CreateAnnotationDetails> createAnnotationDetailsList,
            DataPlaneAPIWrapper dataPlaneAPIWrapper,
            String opcRequestId,
            ExecutorService executorService) {
        return createAnnotationDetailsList.stream()
                .map(
                        createAnnotationDetails ->
                                executorService.submit(
                                        mdcWrap(
                                                taskProvider.getCreateAnnotationTask(
                                                        createAnnotationDetails,
                                                        dataPlaneAPIWrapper,
                                                        opcRequestId))))
                .collect(Collectors.toList());
    }
}