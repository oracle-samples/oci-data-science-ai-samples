import base64
import numpy as np
import os
import pandas as pd
import tarfile
import tensorflow as tf

from transformers import GPT2Tokenizer, TFGPT2Model


model_name = 'tf_model'
tokenize_name = 'vocab'
def load_model(model_file_name=model_name):
    """
    Loads model from the serialized format

    Returns
    -------
    model:  Tensorflow model instance
    """

    model_dir = os.path.dirname(os.path.realpath(__file__))
    
    contents = os.listdir(model_dir)
    if model_file_name + '.h5' in contents:
        model = TFGPT2Model.from_pretrained(model_dir)
        return model
    else:
        raise FileNotFoundError(f'{model_file_name} is not found in model directory {model_dir}.')


def predict(data, model=load_model()):
    """
    Returns prediction given the model and data to predict

    Parameters
    ----------
    model: Model instance returned by load_model API
    data: Data as numpy array

    Returns
    -------
    predictions: Output from scoring server
        Format: {'prediction':output from model.predict method}

    """
    tokenizer_dir = os.path.dirname(os.path.realpath(__file__))
    contents = os.listdir(tokenizer_dir)
    if tokenize_name + '.json' in contents:
        tokenizer = GPT2Tokenizer.from_pretrained(tokenizer_dir)
    
    X = tokenizer(data, return_tensors="tf")
    outputs = model(X)

    last_hidden_state = outputs.last_hidden_state
    pred = last_hidden_state.numpy()[0][0][:4].tolist()
    return {'prediction': pred}
