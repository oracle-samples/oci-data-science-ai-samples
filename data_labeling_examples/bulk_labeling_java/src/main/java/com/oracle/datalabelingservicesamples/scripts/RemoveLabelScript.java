package com.oracle.datalabelingservicesamples.scripts;


import com.oracle.bmc.datalabelingservicedataplane.model.Annotation;
import com.oracle.bmc.datalabelingservicedataplane.model.AnnotationSummary;
import com.oracle.bmc.datalabelingservicedataplane.model.Dataset;
import com.oracle.bmc.datalabelingservicedataplane.model.Entity;
import com.oracle.bmc.datalabelingservicedataplane.model.GenericEntity;
import com.oracle.bmc.datalabelingservicedataplane.model.Label;
import com.oracle.bmc.datalabelingservicedataplane.model.LabelName;
import com.oracle.bmc.datalabelingservicedataplane.model.UpdateAnnotationDetails;
import com.oracle.bmc.datalabelingservicedataplane.requests.DeleteAnnotationRequest;
import com.oracle.bmc.datalabelingservicedataplane.requests.GetAnnotationRequest;
import com.oracle.bmc.datalabelingservicedataplane.requests.GetDatasetRequest;
import com.oracle.bmc.datalabelingservicedataplane.requests.ListAnnotationsRequest;
import com.oracle.bmc.datalabelingservicedataplane.requests.UpdateAnnotationRequest;
import com.oracle.bmc.datalabelingservicedataplane.responses.GetAnnotationResponse;
import com.oracle.bmc.datalabelingservicedataplane.responses.GetDatasetResponse;
import com.oracle.bmc.datalabelingservicedataplane.responses.ListAnnotationsResponse;
import com.oracle.datalabelingservicesamples.requests.Config;
import com.oracle.datalabelingservicesamples.requests.RemoveLabel;
import lombok.extern.slf4j.Slf4j;

import java.security.InvalidParameterException;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.atomic.AtomicInteger;

@Slf4j
public class RemoveLabelScript extends RemoveLabel {

    static Dataset dataset;
    static String removeLabelPrefix;
    static Set<String> actualDatasetLabels = new HashSet<>();
    static Set<String> labelsToRemove = new HashSet<>();
    static ExecutorService executorService;
    static AtomicInteger successCount;
    static AtomicInteger failureCount;

    static {
        executorService = Executors.newFixedThreadPool(Config.INSTANCE.getThreadCount());
        successCount = new AtomicInteger();
        failureCount = new AtomicInteger();
    }

    public static void main(String [] args) throws ExecutionException, InterruptedException {
        log.info("...Starting to remove labels...");
        long startTime = System.nanoTime();
        String datasetId = Config.INSTANCE.getDatasetId();
        validateRequest(datasetId);
        removeLabelPrefix = Config.INSTANCE.getRemoveLabelPrefix();

        if(removeLabelPrefix.equals("*")){
            //delete all annotations
            for (String label : actualDatasetLabels){
                    labelsToRemove.add(label);
            }
        }
        else{
            for (String label : actualDatasetLabels){
                if(label.startsWith(removeLabelPrefix)){
                    labelsToRemove.add(label);
                }
            }
            if(labelsToRemove.isEmpty()){
                log.error("No Label found with prefix {}",removeLabelPrefix );
                throw new InvalidParameterException("Invalid Input RemoveLabelPrefix Provided");
            }
        }
        log.info("Labels to be removed");
        log.info(String.valueOf(labelsToRemove));
        String page = null;

        do{
            ListAnnotationsRequest listAnnotationsRequest = ListAnnotationsRequest.builder().compartmentId(dataset.getCompartmentId()).datasetId(datasetId).lifecycleState(Annotation.LifecycleState.Active).page(page).build();
            ListAnnotationsResponse response = Config.INSTANCE.getDlsDpClient().listAnnotations(listAnnotationsRequest);
            assert response.get__httpStatusCode__() == 200 : "List Annotation Response Fail";

            if(response.getAnnotationCollection().getItems().size()>0){
                List<CompletableFuture<Void>> completableFutures = new ArrayList<>();
                for(AnnotationSummary annotation : response.getAnnotationCollection().getItems()){
                    CompletableFuture<Void> future = CompletableFuture
                            .runAsync(() -> processAnnotationSummaryAndRemoveLabel(annotation),executorService);
                    completableFutures.add(future);
                }
                CompletableFuture<Void> combinedFuture = CompletableFuture
                        .allOf(completableFutures.toArray(new CompletableFuture[0]));
                combinedFuture.get();
            }
            page = response.getOpcNextPage();
        }while(page != null);
        executorService.shutdown();
        log.info("Total annotations to process : {}, "
                        +"Successfully processed {}, "
                        +"Failed to process {}",
                successCount.get() + failureCount.get(),
                successCount.get(),
                failureCount.get());
        long elapsedTime = System.nanoTime() - startTime;
        log.info("Time Taken is {} second(s)", elapsedTime / 1_000_000_000);
    }

    private static void validateRequest(String datasetId) {
        /*
         * Validate Dataset
         */
        GetDatasetRequest getDatasetRequest = GetDatasetRequest.builder().datasetId(datasetId).build();
        GetDatasetResponse datasetResponse = Config.INSTANCE.getDlsDpClient().getDataset(getDatasetRequest);
        assert datasetResponse.get__httpStatusCode__() == 200 : "Invalid Dataset Id Provided";
        List<LabelName> datasetLabelSet = datasetResponse.getDataset().getLabelSet().getItems();

        log.info("Dataset Labels : ");
        for (LabelName labelName : datasetLabelSet) {
            actualDatasetLabels.add(labelName.getName());
            log.info(labelName.getName());
        }
        dataset = datasetResponse.getDataset();
    }
    private static void processAnnotationSummaryAndRemoveLabel(AnnotationSummary annotationSummary){
        GetAnnotationRequest getAnnotationRequest = GetAnnotationRequest.builder().annotationId(annotationSummary.getId()).build();
        GetAnnotationResponse response = Config.INSTANCE.getDlsDpClient().getAnnotation(getAnnotationRequest);
        assert response.get__httpStatusCode__() == 200 : "GetAnnotation Request Failed";

        List<Entity> entityList = response.getAnnotation().getEntities();
        if (entityList.size() > 1) {
            log.error("Single/Multi label annotation can have only one annotation entity");
            return;
        }

        for (Entity entity : entityList) {
            if (entity instanceof GenericEntity) {
                GenericEntity genericEntity = (GenericEntity) entity;
                List<Label> entityLabels = genericEntity.getLabels();
                List<Label> newLabelList = new ArrayList<>();
                for(Label label : entityLabels){
                    if(!labelsToRemove.contains(label.getLabel())){
                        newLabelList.add(label);
                    }
                }
                if(newLabelList.isEmpty()){
                    deleteAnnotation(response.getAnnotation().getId());
                }
                else if(newLabelList.equals(entityLabels)){
                    log.info("Nothing to update");
                }
                else{
                    GenericEntity newEntity = GenericEntity.builder().labels(newLabelList).extendedMetadata(genericEntity.getExtendedMetadata()).build();
                    updateAnnotation(response.getAnnotation(),newEntity);
                }
            }
        }
    }
    private static void updateAnnotation(Annotation annotation, Entity entity){
        List<Entity> entityList = new ArrayList<>();
        entityList.add(entity);
        try {
            UpdateAnnotationDetails updateAnnotationDetails = UpdateAnnotationDetails.builder().definedTags(annotation.getDefinedTags()).freeformTags(annotation.getFreeformTags()).entities(entityList).build();
            UpdateAnnotationRequest updateAnnotationRequest = UpdateAnnotationRequest.builder().annotationId(annotation.getId()).updateAnnotationDetails(updateAnnotationDetails).build();
            Config.INSTANCE.getDlsDpClient().updateAnnotation(updateAnnotationRequest);
            successCount.incrementAndGet();
        }catch(Exception e){
            log.error("Exception in update annotation");
            failureCount.incrementAndGet();

        }
    }
    private static void deleteAnnotation(String annotationId){
        try {
            DeleteAnnotationRequest deleteAnnotationRequest = DeleteAnnotationRequest.builder().annotationId(annotationId).build();
            Config.INSTANCE.getDlsDpClient().deleteAnnotation(deleteAnnotationRequest);
            successCount.incrementAndGet();
        } catch (Exception e){
            log.error("Exception in delete annotation");
            failureCount.incrementAndGet();
        }
    }
}
