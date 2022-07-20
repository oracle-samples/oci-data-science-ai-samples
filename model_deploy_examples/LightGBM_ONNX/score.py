import json
import numpy as np
import onnxruntime as rt
import os
import pandas as pd
from sklearn.preprocessing import LabelEncoder
model_name = 'model.onnx'
transformer_name = 'onnx_data_transformer.json'
"""
   Inference script. This script is used for prediction by scoring server when schema is known.
"""
def load_model(model_file_name=model_name):
    """
    Loads model from the serialized format

    Returns
    -------
    model:  an onnxruntime session instance
    """
    model_dir = os.path.dirname(os.path.realpath(__file__))
    contents = os.listdir(model_dir)
    if model_file_name in contents:
        return rt.InferenceSession(os.path.join(model_dir, model_file_name))
    else:
        raise Exception('{0} is not found in model directory {1}'.format(model_file_name, model_dir))
def predict(data, model=load_model()):
    """
    Returns prediction given the model and data to predict

    Parameters
    ----------
    model: Model session instance returned by load_model API
    data: Data format as expected by the onnxruntime API

    Returns
    -------
    predictions: Output from scoring server
        Format: {'prediction':output from model.predict method}

    """
    from pandas import read_json, DataFrame
    from io import StringIO
    X = read_json(StringIO(data)) if isinstance(data, str) else DataFrame.from_dict(data)
    model_dir = os.path.dirname(os.path.realpath(__file__))
    contents = os.listdir(model_dir)
    # Note: User may need to edit this
    if transformer_name in contents:
        onnx_data_transformer = ONNXTransformer.load(os.path.join(model_dir, transformer_name))
        X, _ = onnx_data_transformer.transform(X)
    else:
        onnx_data_transformer = None
    
    onnx_transformed_rows = []
    for name, row in X.iterrows():
        onnx_transformed_rows.append(list(row))
    input_data = {'input': onnx_transformed_rows}
    
    pred = model.run(None, input_data)[0].tolist()
    return {'prediction':pred}
class ONNXTransformer(object):
    """
    This is a transformer to convert X [pandas.Dataframe, dask.Dataframe, equivalent] and y [array like] data into Onnx
    readable dtypes and formats. It is Serializable, so it can be reloaded at another time.

    Usage:
    >>> from ads.common.model_export_util import ONNXTransformer
    >>> onnx_data_transformer = ONNXTransformer(task="classification")
    >>> train_transformed = onnx_data_transformer.fit_transform(train.X, train.y)
    >>> test_transformed = onnx_data_transformer.transform(test.X, test.y)

    Parameters
    ----------
    task: str
        Either "classification" or "regression". This determines if y should be label encoded
    """
    def __init__(self, task=None):
        self.task = task
        self.cat_impute_values = {}
        self.cat_unique_values = {}
        self.label_encoder = None
        self.dtypes = None
        self._fitted = False
    def _handle_dtypes(self, X):
        # Data type cast could be expensive doing it in for loop
        # Especially with wide datasets
        # So cast the numerical columns first, without loop
        # Then impute categorical columns
        dict_astype = {}
        for k, v in zip(X.columns, X.dtypes):
            if v in ['int64', 'int32', 'int16', 'int8'] or 'float' in str(v):
                dict_astype[k] = 'float32'
        _X = X.astype(dict_astype)
        for k in _X.columns[_X.dtypes != 'float32']:
            # SimpleImputer is not available for strings in ONNX-ML specifications
            # Replace NaNs with the most frequent category
            self.cat_impute_values[k] = _X[k].value_counts().idxmax()
            _X[k] = _X[k].fillna(self.cat_impute_values[k])
            # Sklearn's OrdinalEncoder and LabelEncoder don't support unseen categories in test data
            # Label encode them to identify new categories in test data
            self.cat_unique_values[k] = _X[k].unique()
        return _X
    def fit(self, X, y=None):
        _X = self._handle_dtypes(X)
        self.dtypes = _X.dtypes
        if self.task == 'classification' and y is not None:
            # Label encoding is required for SVC's onnx converter
            self.label_encoder = LabelEncoder()
            y = self.label_encoder.fit_transform(y)

        self._fitted = True
        return self
    def transform(self, X, y=None):
        assert self._fitted, 'Call fit_transform first!'
        # Data type cast could be expensive doing it in for loop
        # Especially with wide datasets
        # So cast the numerical columns first, without loop
        # Then impute categorical columns
        _X = X.astype(self.dtypes)
        for k in _X.columns[_X.dtypes != 'float32']:
            # Replace unseen categories with NaNs and impute them
            _X.loc[~_X[k].isin(self.cat_unique_values[k]), k] = np.nan
            # SimpleImputer is not available for strings in ONNX-ML specifications
            # Replace NaNs with the most frequent category
            _X[k] = _X[k].fillna(self.cat_impute_values[k])

        if self.label_encoder is not None and y is not None:
            y = self.label_encoder.transform(y)

        return _X, y
    def fit_transform(self, X, y=None):
        return self.fit(X, y).transform(X, y)
    def save(self, filename, **kwargs):
        export_dict = {
            "task": {"value": self.task, "dtype": str(type(self.task))},
            "cat_impute_values": {"value": self.cat_impute_values, "dtype": str(type(self.cat_impute_values))},
            "cat_unique_values": {"value": self.cat_unique_values, "dtype": str(type(self.cat_unique_values))},
            "label_encoder": {"value": {
                "params": self.label_encoder.get_params() if
                hasattr(self.label_encoder, "get_params") else {},
                "classes_": self.label_encoder.classes_.tolist() if
                hasattr(self.label_encoder, "classes_") else []},
                "dtype": str(type(self.label_encoder))},
            "dtypes": {"value": {"index": list(self.dtypes.index), "values": [str(val) for val in self.dtypes.values]}
            if self.dtypes is not None else {},
                       "dtype": str(type(self.dtypes))},
            "_fitted": {"value": self._fitted, "dtype": str(type(self._fitted))}
        }
        with open(filename, 'w') as f:
            json.dump(export_dict, f, sort_keys=True, indent=4, separators=(',', ': '))
    @staticmethod
    def load(filename, **kwargs):
        # Make sure you have  pandas, numpy, and sklearn imported
        with open(filename, 'r') as f:
            export_dict = json.load(f)
        try:
            onnx_transformer = ONNXTransformer(task=export_dict['task']['value'])
        except Exception as e:
            print(f"No task set in ONNXTransformer at {filename}")
            raise e
        for key in export_dict.keys():
            if key not in ["task", "label_encoder", "dtypes"]:
                try:
                    setattr(onnx_transformer, key, export_dict[key]["value"])
                except Exception as e:
                    print(f"Warning: Failed to reload from {filename} to OnnxTransformer.")
                    raise e
        onnx_transformer.dtypes = pd.Series(data=[np.dtype(val) for val in export_dict["dtypes"]["value"]["values"]], index=export_dict["dtypes"]["value"]["index"])
        le = LabelEncoder()
        le.set_params(**export_dict["label_encoder"]["value"]["params"])
        le.classes_ = np.asarray(export_dict["label_encoder"]["value"]["classes_"])
        onnx_transformer.label_encoder = le
        return onnx_transformer