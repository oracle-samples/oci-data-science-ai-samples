package com.oracle.datalabelingservicesamples.modelTraining;

import com.oracle.datalabelingservicesamples.requests.AssistedLabelingParams;

public interface ModelTrainingWrapper {
    public void performModelTraining(AssistedLabelingParams assistedLabelingParams) throws Exception;
}
