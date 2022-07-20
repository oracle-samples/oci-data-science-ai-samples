import os
import pandas as pd
import tensorflow as tf
import tensorflow.keras as keras
import numpy as np
from tensorflow.keras.models import load_model as klm

# Insert the name of your model here.
# For example: "my-model.hdf5"
model_name = "model.hdf5"
 
def load_model(model_file_name=model_name):
    """
    Loads model from the serialized format
 
    Returns
    -------
    model:  a model instance on which predict API can be invoked
    """
    model_dir = os.path.dirname(os.path.realpath(__file__))
    contents = os.listdir(model_dir)
    if model_file_name in contents:
        return klm(os.path.join(model_dir, model_file_name))
    else:
        raise FileNotFoundError(f'{model_file_name} is not found in model directory {model_dir}.')
 
def predict(data, model=load_model()):
    """
    Returns prediction given the model and data to predict
 
    Parameters
    ----------
    model: Model instance returned by load_model API
    data: Data format as expected by Keras API
 
    Returns
    -------
    predictions: Output from scoring server
        Format: {'prediction':output from model.predict method}
 
    """
    X = pd.DataFrame.from_dict(data).to_numpy()
    pred = model.predict(X).tolist()
    return {'prediction': pred}