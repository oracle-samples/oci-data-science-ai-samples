"""
    This boilerplate is based on a n sklearn model serialized with cloudpickle.
"""
import json
import os
from cloudpickle import cloudpickle

"""
    You can provide your own model object and your own serialization library (e.g. pickle, onnx, etc).
    If no model is specified then predict() by default will return 'Hello World!'
"""


model_name = f"<replace-with-your-model-name>"


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
    if not model_file_name:
        raise ValueError('model_file_name cannot be None')

    # This is the default implementation of the load_model() specific to this score.py template only.
    if model_file_name == "<replace-with-your-model-name>":
        return "default_model"

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

    # This is the default implementation of the predict() function specific to this score.py template only.
    if model == "default_model" or len(data) == 0:
        return {'prediction':'Hello world!'}

    from pandas import read_json, DataFrame
    from io import StringIO
    data = read_json(StringIO(data)) if isinstance(data, str) else DataFrame.from_dict(data)
    pred = model.predict(data).tolist()
    return {'prediction': pred}
