"""
    This boilerplate is based on a n sklearn model serialized with cloudpickle.
"""
import json
import os
from cloudpickle import cloudpickle

"""
    Replace with your own model object and your own serialization library (e.g. pickle, onnx, etc).
"""
model_name = 'model.pkl'


"""
   Inference script. This script is used for prediction by scoring server when schema is known.
"""


def load_model(model_file_name=model_name):
    """
    Loads model from the serialized format
    WARNING: Please use the same library to load the model which was used to serialise it.
    Using a different library will result in unexpected behavior.
    Returns
    -------
    model:  a model instance on which predict API can be invoked
    """
    model_dir = os.path.dirname(os.path.realpath(__file__))
    contents = os.listdir(model_dir)
    # --------------------------WARNING-------------------------
    #  Please use the same library to load the model which was used to serialise it.
    #  Using a different library will result in unexpected behavior.
    # -----------------------------------------------------------
    if model_file_name in contents:
        with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), model_file_name), "rb") as file:
            return cloudpickle.load(file)
    else:
        raise Exception('{0} is not found in model directory {1}'.format(model_file_name, model_dir))


def predict(data, model=load_model()):
    """
    Returns prediction given the model and data to predict
    Parameters
    ----------
    model: Model instance returned by load_model API
    data: Data format as expected by the predict API of the core estimator. For eg. in case of sckit models it could be numpy array/List of list/Panda DataFrame
    Returns
    -------
    predictions: Output from scoring server
        Format: {'prediction':output from model.predict method}
    """
    from pandas import read_json, DataFrame
    from io import StringIO
    data = read_json(StringIO(data)) if isinstance(data, str) else DataFrame.from_dict(data)
    pred = model.predict(data).tolist()
    return {'prediction': pred}
