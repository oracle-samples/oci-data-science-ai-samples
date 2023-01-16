package com.oracle.datalabelingservicesamples.utils;

import com.google.common.collect.ImmutableSet;
import com.oracle.pic.commons.id.Id;
import com.oracle.pic.commons.id.InvalidOCIDException;
import com.oracle.pic.commons.id.OCIDParser;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang3.StringUtils;
import com.oracle.pic.commons.exceptions.server.ErrorCode;
import com.oracle.pic.commons.exceptions.server.RenderableException;

import java.util.Set;

import static java.lang.Float.parseFloat;

@Slf4j
public class InputValidator {

    private static final Set<String> mlModelTypes =
            ImmutableSet.of(
                    "PRETRAINED",
                    "CUSTOM",
                    "NEW");

    private static final Set<String> labelingAlgorithms =
            ImmutableSet.of(
                    "FIRST_LETTER_MATCH",
                    "FIRST_REGEX_MATCH",
                    "CUSTOM_LABELS_MATCH",
                    "ML_ASSISTED_LABELING");

    public void validateRequiredParameter(String parameterName, String parameterValue) {
        if (StringUtils.isBlank(parameterValue)) {
            log.error("Invalid required parameter: {} value cannot be empty.", parameterName);
            throw new RenderableException(ErrorCode.InvalidParameter, "Invalid %s", parameterName);
        }
    }

    public void validateMlModelType(String modelType) {
        if(!mlModelTypes.contains(modelType)) {
            log.error("Invalid Ml model type - Options are PRETRAINED, CUSTOM, NEW");
            throw new RenderableException(ErrorCode.InvalidParameter, "Invalid mlModelType");
        }
    }

    public void validateLabelingAlgorithm(String labelingAlgorithm) {
        if(!labelingAlgorithms.contains(labelingAlgorithm)) {
            log.error("Invalid labeling algorithm - to use this script set to ML_ASSISTED_LABELING");
            throw new RenderableException(ErrorCode.InvalidParameter, "Invalid labelingAlgorithm");
        }
    }

    public void validateConfidenceScoreThreshold(String confidenceScore) {
        float confidenceThreshold;
        try{
            confidenceThreshold = parseFloat(confidenceScore);
        } catch(NumberFormatException e){
            log.error("Invalid confidence score, score should be valid decimal between 0.0 and 1.0");
            throw new RenderableException(ErrorCode.InvalidParameter, "Invalid confidenceThreshold");
        }

        if (confidenceThreshold < 0.0F || confidenceThreshold > 1.0F) {
            log.error("Invalid confidence score, score should be valid decimal between 0.0 and 1.0");
            throw new RenderableException(ErrorCode.InvalidParameter, "Invalid confidenceThreshold");
        }
    }

    public void isValidResourceOcid(String ocid, Set<String> entityTypes, String resourceName) {
        if (ocid == null) {
            throw new RenderableException(ErrorCode.InvalidParameter, "Ocid cannot be null");
        }
        Id id;
        try {
            id = OCIDParser.fromString(ocid);
        } catch (InvalidOCIDException e) {
            // Input was not an ocid.
            log.error("Invalid OCID for {}", resourceName);
            throw new RenderableException(ErrorCode.InvalidParameter, "Invalid ocid");
        }
        // Sanity check in case parsing the ocid ever returned a null value.
        if (id == null) {
            log.error("Invalid OCID for {}", resourceName);
            throw new RenderableException(ErrorCode.InvalidParameter, "Invalid ocid");
        }
        // If there's no given entity type then we don't need to check any further.
        if (entityTypes == null) {
            return;
        }
        if (!entityTypes.contains(id.getEntityType().getName()) ) {
            log.error("Invalid OCID entity type for {}", resourceName);
            throw new RenderableException(ErrorCode.InvalidParameter, "Invalid ocid entity type");
        }
    }
}
