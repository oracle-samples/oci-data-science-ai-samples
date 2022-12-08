package com.oracle.datalabelingservicesamples.utils;

import com.google.common.collect.ImmutableSet;
import com.oracle.pic.commons.id.Id;
import com.oracle.pic.commons.id.InvalidOCIDException;
import com.oracle.pic.commons.id.OCIDParser;
import com.oracle.pic.commons.util.EntityType;
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
            throw new RenderableException(ErrorCode.InvalidParameter, "Invalid %s", parameterName);
        }
    }

    public void validateOptionalParameter(String parameterName, String parameterValue) {
        if (parameterValue == null) {
            return;
        }
        if (StringUtils.isBlank(parameterValue)) {
            throw new RenderableException(ErrorCode.InvalidParameter, "Invalid %s", parameterName);
        }
    }

    public void validateMlModelType(String modelType) {
        if(!mlModelTypes.contains(modelType)) {
            throw new RenderableException(ErrorCode.InvalidParameter, "Invalid Ml model type");
        }
    }

    public void validateLabelingAlgorithm(String labelingAlgorithm) {
        if(!labelingAlgorithms.contains(labelingAlgorithm)) {
            throw new RenderableException(ErrorCode.InvalidParameter, "Invalid labelingAlgorithm");
        }
    }

    public void validateConfidenceScoreThreshold(String confidenceScore) {
        float confidenceThreshold;
        try{
            confidenceThreshold = parseFloat(confidenceScore);
        } catch(NumberFormatException e){
            throw new RenderableException(ErrorCode.InvalidParameter, "Invalid confidence threshold");
        }

        if (confidenceThreshold < 0.0F || confidenceThreshold > 1.0F) {
            throw new RenderableException(ErrorCode.InvalidParameter, "Invalid confidence threshold, score should be between 0 and 1");
        }
    }

    public void isValidResourceOcid(String ocid, Set<String> entityTypes) {
        if (ocid == null) {
            throw new RenderableException(ErrorCode.InvalidParameter, "Ocid cannot be null");
        }
        Id id;
        try {
            id = OCIDParser.fromString(ocid);
        } catch (InvalidOCIDException e) {
            // Input was not an ocid.
            throw new RenderableException(ErrorCode.InvalidParameter, "Invalid ocid");
        }
        // Sanity check in case parsing the ocid ever returned a null value.
        if (id == null) {
            throw new RenderableException(ErrorCode.InvalidParameter, "Invalid ocid");
        }
        // If there's no given entity type then we don't need to check any further.
        if (entityTypes == null) {
            return;
        }
        if (!entityTypes.contains(id.getEntityType().getName()) ) {
            throw new RenderableException(ErrorCode.InvalidParameter, "Invalid ocid entity type");
        }
    }
}
