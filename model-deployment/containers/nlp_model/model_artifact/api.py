# We now need the json library so we can load and export json data
import json
import os
import numpy as np
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.neural_network import MLPClassifier
import pandas as pd
from joblib import load
from sklearn import preprocessing
import logging

from flask import Flask, request

# Set environnment variables
WORK_DIRECTORY = os.environ["WORK_DIRECTORY"]
TEST_DATA = os.path.join(WORK_DIRECTORY, "test.json")
MODEL_DIR = os.environ["MODEL_DIR"]
MODEL_FILE_LDA = os.environ["MODEL_FILE_LDA"]
MODEL_PATH_LDA = os.path.join(MODEL_DIR, MODEL_FILE_LDA)

# Loading LDA model
print("Loading model from: {}".format(MODEL_PATH_LDA))
inference_lda = load(MODEL_PATH_LDA)

# Creation of the Flask app
app = Flask(__name__)


# API 1
# Flask route so that we can serve HTTP traffic on that route
@app.route('/health')
# Get data from json and return the requested row defined by the variable Line
def health():
    # We can then find the data for the requested row and send it back as json
    return {"status": "success"}

# API 2
# Flask route so that we can serve HTTP traffic on that route
@app.route('/predict',methods=['POST'])
# Return prediction for both Neural Network and LDA inference model with the requested row as input
def prediction():
    data = pd.read_json(TEST_DATA)
    request_data = request.get_data()
    print(request_data)
    print(type(request_data))
    if isinstance(request_data, bytes):
        print("Data is of type bytes")
        request_data = request_data.decode("utf-8")
    print(request_data)
    line = json.loads(request_data)['line']
    data_test = data.transpose()
    X = data_test.drop(data_test.loc[:, 'Line':'# Letter'].columns, axis = 1)
    X_test = X.iloc[int(line),:].values.reshape(1, -1)

    clf_lda = load(MODEL_PATH_LDA)
    prediction_lda = clf_lda.predict(X_test)

    return {'prediction LDA': int(prediction_lda)}


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port = 5000)
