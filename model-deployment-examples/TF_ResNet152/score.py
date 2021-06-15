import numpy as np
import os
import pandas as pd
import tarfile
import tensorflow as tf
from tempfile import TemporaryDirectory
import base64
from PIL import Image
import io

Image.MAX_IMAGE_PIXELS = None

model_name = 'TF_ResNet152'

def load_model(model_file_name=model_name):
    """
    Loads model from the serialized format

    Returns
    -------
    model:  Tensorflow model instance
    """
    model_dir = os.path.dirname(os.path.realpath(__file__))
    contents = os.listdir(model_dir)
    if model_file_name + '.tar.gz' in contents:
        with TemporaryDirectory() as tmpdir: 
            tmp_path = os.path.join(tmpdir, model_file_name)
            with tarfile.open(os.path.join(model_dir, model_file_name + '.tar.gz'), 'r') as tar:
                tar.extractall(path=tmp_path)
            model = tf.saved_model.load(tmp_path)
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
    img_bytes = io.BytesIO(base64.b64decode(data.encode('utf-8')))
    image = Image.open(img_bytes).resize((224, 224))
    X = tf.image.convert_image_dtype(np.array(image), dtype=tf.float32)
    pred = str(tf.argmax(model(X[np.newaxis, :, :, :])[0], axis=-1).numpy())
    return {'prediction': pred}
