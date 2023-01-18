package com.oracle.datalabelingservicesamples.labelingstrategies;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.oracle.bmc.aivision.model.AnalyzeImageResult;
import com.oracle.bmc.aivision.model.CreateImageJobDetails;
import com.oracle.bmc.aivision.model.ImageClassificationFeature;
import com.oracle.bmc.aivision.model.ImageFeature;
import com.oracle.bmc.aivision.model.ImageJob;
import com.oracle.bmc.aivision.model.InputLocation;
import com.oracle.bmc.aivision.model.ObjectListInlineInputLocation;
import com.oracle.bmc.aivision.model.ObjectLocation;
import com.oracle.bmc.aivision.model.OutputLocation;
import com.oracle.bmc.aivision.requests.CreateImageJobRequest;
import com.oracle.bmc.aivision.requests.GetImageJobRequest;
import com.oracle.bmc.datalabelingservicedataplane.model.CreateAnnotationDetails;
import com.oracle.bmc.datalabelingservicedataplane.model.Entity;
import com.oracle.bmc.datalabelingservicedataplane.model.GenericEntity;
import com.oracle.bmc.datalabelingservicedataplane.model.Label;
import com.oracle.bmc.datalabelingservicedataplane.model.RecordSummary;
import com.oracle.bmc.model.BmcException;
import com.oracle.bmc.model.Range;
import com.oracle.bmc.objectstorage.requests.GetObjectRequest;
import com.oracle.bmc.objectstorage.responses.GetObjectResponse;
import com.oracle.bmc.retrier.RetryConfiguration;
import com.oracle.bmc.waiter.MaxAttemptsTerminationStrategy;
import com.oracle.datalabelingservicesamples.requests.AssistedLabelingParams;
import com.oracle.datalabelingservicesamples.requests.BucketDetails;
import com.oracle.datalabelingservicesamples.requests.Config;
import com.oracle.datalabelingservicesamples.requests.ObjectDetails;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.collections4.CollectionUtils;
import org.apache.commons.io.IOUtils;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Optional;

@Slf4j
public class MlAssistedImageClassification implements MlAssistedLabelingStrategy {
    @Override
    public List<CreateAnnotationDetails> bulkAnalyzeRecords(List<RecordSummary> recordSummaries, AssistedLabelingParams assistedLabelingParams) throws Exception {

        List<ImageFeature> imageJobFeatureList = new ArrayList<>();
        imageJobFeatureList.add(
                ImageClassificationFeature.builder()
                        .maxResults(10)
                        .modelId(assistedLabelingParams.getCustomModelId())
                        .build());

        List<ObjectLocation> imageObjectLocations = new ArrayList<>();
        for (RecordSummary recordSummary : recordSummaries) {
            imageObjectLocations.add(
                    ObjectLocation.builder()
                            .namespaceName(assistedLabelingParams.getCustomerBucket().getNamespace())
                            .bucketName(assistedLabelingParams.getCustomerBucket().getBucketName())
                            .objectName(recordSummary.getName())
                            .build());
        }

        InputLocation imageJobInput =
                ObjectListInlineInputLocation.builder()
                        .objectLocations(imageObjectLocations)
                        .build();

        OutputLocation imageJobOutput =
                OutputLocation.builder()
                        .namespaceName(assistedLabelingParams.getCustomerBucket().getNamespace())
                        .bucketName(assistedLabelingParams.getCustomerBucket().getBucketName())
                        .prefix(OUTPUT_LOCATION_PREFIX + "/")
                        .build();

        CreateImageJobDetails createImageJobDetails =
                CreateImageJobDetails.builder()
                        .compartmentId(assistedLabelingParams.getCompartmentId())
                        .features(imageJobFeatureList)
                        .inputLocation(imageJobInput)
                        .isZipOutputEnabled(false)
                        .outputLocation(imageJobOutput)
                        .build();

        CreateImageJobRequest createImageJobRequest =
                CreateImageJobRequest.builder()
                        .createImageJobDetails(createImageJobDetails)
                        .build();
        GetImageJobRequest getImageJobRequest;
        String jobID;
        try {
            jobID = Config.INSTANCE.getAiVisionClient().createImageJob(createImageJobRequest).getImageJob().getId();
            getImageJobRequest = GetImageJobRequest.builder().imageJobId(jobID).build();
            log.info("Vision JobId {}", jobID);
        } catch (Exception ex) {
            log.error("Error occurred during vision job {}", ex.getMessage());
            throw new Exception(ex);
        }

        // Poll for job's completeness
        ImageJob.LifecycleState jobStatus =
                Config.INSTANCE.getAiVisionClient().getImageJob(getImageJobRequest).getImageJob().getLifecycleState();
        while (jobStatus.equals(ImageJob.LifecycleState.InProgress)
                || jobStatus.equals(ImageJob.LifecycleState.Accepted)) {
            Thread.sleep(3000);
            jobStatus =
                    Config.INSTANCE.getAiVisionClient().getImageJob(getImageJobRequest).getImageJob().getLifecycleState();
        }
        OutputLocation location = null;
        if (jobStatus.equals(ImageJob.LifecycleState.Succeeded)) {
            location =
                    Config.INSTANCE.getAiVisionClient().getImageJob(getImageJobRequest).getImageJob().getOutputLocation();
            log.info("Vision service job succeeded {}", location.getBucketName());

        } else {
            log.error("Vision job status {}", jobStatus.getValue());
            throw new Exception("Vision call didn't succeed");
        }
        //
        List<CreateAnnotationDetails> createAnnotationDetails = new ArrayList<>();
        BucketDetails bucketDetails =
                BucketDetails.builder()
                        .bucketName(location.getBucketName())
                        .namespace(location.getNamespaceName())
                        .prefix(location.getPrefix() + jobID + "/")
                        .region(Config.INSTANCE.getRegion())
                        .build();
        for (RecordSummary recordSummary : recordSummaries) {
            try {
                // for each record find an equivalent object in the outputlocation
                String recordID = recordSummary.getId();
                String objectName =
                        String.format(
                                "%s_%s_%s.json",
                                location.getNamespaceName(),
                                location.getBucketName(),
                                recordSummary.getName());

                Thread.sleep(5000);
                ObjectDetails objectDetails =
                        getObjectDetails(
                                location.getPrefix() + jobID + "/" + objectName,
                                bucketDetails,
                                Optional.ofNullable(null),
                                Optional.ofNullable(null),
                                Optional.empty());
//                String objectDetailsContextModified = objectDetails.getContentString().replace("\"detectedFaces\":[],", "");
                AnalyzeImageResult analyzeImageResult =
                        new ObjectMapper()
                                .readValue(
                                        objectDetails.getContentString(), AnalyzeImageResult.class);
                log.debug("Labels predicted by the vision model :{}",analyzeImageResult.getLabels());
                if (analyzeImageResult.getLabels() != null) {
                    List<Entity> entities =
                            mapToDLSEntities(
                                    assistedLabelingParams.getDlsDatasetLabels(),
                                    analyzeImageResult.getLabels(),
                                    assistedLabelingParams.getAnnotationFormat(),
                                    assistedLabelingParams.getConfidenceThreshold());
                    if (!entities.isEmpty()) {
                        createAnnotationDetails.add(
                                new CreateAnnotationDetails(
                                        recordID,
                                        assistedLabelingParams.getCompartmentId(),
                                        entities,
                                        null,
                                        null));
                    }
                }
            } catch (Exception e) {
                log.info("Error occurred in vision wrapper");
                throw e;
            }
        }return createAnnotationDetails;
    }

    public List<Entity> mapToDLSEntities(List<String> dlsLabels, List<com.oracle.bmc.aivision.model.Label> visionLabels,
                                         String annotationFormat, float confidenceThreshold) {
        List<Entity> imageClassificationEntities = new ArrayList<>();
        List<Label> labels = new ArrayList<>();
        dlsLabels = Collections.unmodifiableList(dlsLabels);
        List<String> dlsLabelsLowercase = (List<String>) CollectionUtils.collect(dlsLabels,
                String::toLowerCase);
        dlsLabelsLowercase = Collections.unmodifiableList(dlsLabelsLowercase);
        for (com.oracle.bmc.aivision.model.Label visionLabel : visionLabels) {
            if (dlsLabelsLowercase.contains(visionLabel.getName().toLowerCase())
                    && visionLabel.getConfidence() >= confidenceThreshold) {
                int indexOfLabel = dlsLabelsLowercase.indexOf(visionLabel.getName().toLowerCase());
                labels.add(
                        Label.builder()
                                .label(dlsLabels.get(indexOfLabel))
                                .build());
            }
        }
        GenericEntity imageClassificationEntity = null;
        if(annotationFormat.equalsIgnoreCase("SINGLE_LABEL")){
            if(!labels.isEmpty()) {
                imageClassificationEntity =
                        GenericEntity.builder()
                                .labels(Collections.singletonList(labels.get(0)))
                                .build();
            }
        }
        else if(annotationFormat.equalsIgnoreCase("MULTI_LABEL")){
            if(!labels.isEmpty()) {
                imageClassificationEntity =
                        GenericEntity.builder()
                                .labels(labels)
                                .build();
            }
        }
        imageClassificationEntities.add(imageClassificationEntity);
        return imageClassificationEntities;
    }

    public ObjectDetails getObjectDetails(
            String objectName,
            BucketDetails bucketDetails,
            Optional<String> etag,
            Optional<String> opcClientRequestId,
            Optional<String> byteRange)
            throws Exception {
        try {
            Range range = null;
            if (byteRange.isPresent()) {
                range = Range.parse(byteRange.get());
            }
            GetObjectRequest.Builder requestBuilder =
                    GetObjectRequest.builder()
                            .namespaceName(bucketDetails.getNamespace())
                            .bucketName(bucketDetails.getBucketName())
                            .range(range)
                            .retryConfiguration(RetryConfiguration.builder()
                                    .terminationStrategy(new MaxAttemptsTerminationStrategy(3))
                                    .build())
                            .objectName(objectName);

            opcClientRequestId.ifPresent(value -> requestBuilder.opcClientRequestId(value));
            etag.ifPresent(value -> requestBuilder.ifNoneMatch(value));

            GetObjectResponse response = Config.INSTANCE.getObjectStorageClient().getObject(requestBuilder.build());
            int statusCode = response.get__httpStatusCode__();
            if (statusCode != 200 && statusCode != 304 && statusCode != 206) {
                log.error("Object storage response {}", response);
                throw new Exception("Object storage access failed with status code "+statusCode);
            }

            ObjectDetails objectDetails =
                    ObjectDetails.builder()
                            .name(objectName)
                            .etag(response.getETag())
                            .content(new byte[0])
                            .build();

            if (!response.isNotModified()) {
                byte[] content = IOUtils.toByteArray(response.getInputStream());
                objectDetails.setContent(content);
                objectDetails.setContentLength(content.length);
                objectDetails.setContentType(response.getContentType());
            }

            return objectDetails;
        } catch (BmcException e) {
            log.error("BmcException occurred while accessing ObjectStorage bucket.", e);
        } catch (Exception e) {
            log.error("Exception occurred while accessing ObjectStorage bucket.", e);
        }
        return null;
    }

}
