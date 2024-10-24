"""Module for invoking the apps in OCI Data Science Model Deployment.

This module is designed to handle the invoking of user apps.
Each app should be an individual python module containing an invoke() function.

When using this module, the payload of the POST request should have the following format:
{
    "module": "The relative path of the file containing the invoke() function for the app.",
    "inputs": "The inputs to the invoke() function.",
    "async": "The object storage location for saving the results of the the invoke() call.",
    "id": "An ID for identifying the request. The same ID will be returned in the response.",
}

The response will have the following format:
{
    "outputs": "The outputs returned by invoking the app/model",
    "error": "Error message, if any.",
    "traceback": "Traceback, if any.",
    "id": "The ID for identifying the request.",
}

While the `inputs` key is required for all requests, `module`, `async` and `id` are optional.

If `module` is not specified, "app.py" will be used.
Alternatively, you can set it with the DEFAULT_MODULE environment variable.
Make sure you have the modules saved into the model catalog as part of the model artifact.
For debugging purpose, you can also set the environment variable ENABLE_OBJECT_STORAGE_MODULE=1
to enable loading module from OCI object storage.
This will allow you to load new modules without creating new deployment.
For example:
{
    "module": "oci://bucket@namespace/prefix/to/module.py",
    "inputs": "We have a dream.",
}
Keep in mind that enabling this option can be a security risk
as it allows users to load and run any files from object storage.

If the `async` option is specified, the invoke() will be called in a separated thread
and the response will be sent without waiting for the invoke() call to be completed.
This is useful for invoke() calls that require more than 60 second.
The value of `async` should be a location on OCI object storage.
The results of the invoke() call will be save into the object storage as a JSON file.
In the response, the value of the `outputs` will be the uri of the JSON file.
You can check if the invoke() call has been completed by checking if the file exists.

The `id` in the payload allows you to track the request/response.
The same `id` will be included in the response if specified.
If `id` is not specified, a new UUID4 will be generated.

"""

import importlib.util
import json
import os
import sys
import tempfile
import traceback
import uuid

from threading import Thread
from typing import Any, Union, Optional

import fsspec


# This is a dictionary mapping the module filename to the MD5 of the modules.
hash_map = {}
# This is a dictionary mapping the module filename to loaded models
models = {}


DEFAULT_MODULE = os.environ.get("DEFAULT_MODULE", "app.py")
ENABLE_OBJECT_STORAGE_MODULE = os.environ.get("ENABLE_OBJECT_STORAGE_MODULE", False)


def import_from_path(file_path: str, module_name: Optional[str] = None):
    """Imports a module from file path.

    https://docs.python.org/3/library/importlib.html#importing-a-source-file-directly

    Parameters
    ----------
    file_path : str
        The relative path of the python module containing the invoke() function.
    module_name : str, optional
        The name for the module, by default None.
        If this is not specified, it will be set to the same as the file_path.
        The module_name should be unique in the environment.

    Returns
    -------
    ModuleType
        The imported module
    """
    if not module_name:
        module_name = file_path
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def check_hash(module_file: str) -> None:
    """Checks the MD5 of a module if it is from object storage.
    If the MD5 is not the same as the cached module, invalidate the cache.
    """
    if module_file.startswith("oci://"):
        print(f"Checking the MD5 of {module_file}")
        fs = fsspec.filesystem("oci")
        fs.invalidate_cache()
        md5 = fs.ukey(module_file)
        if md5 != hash_map.get(module_file):
            print(f"Found updated file: {module_file}.")
            models.pop(module_file, None)


def load_model(module_file: str = DEFAULT_MODULE):
    """Loads the model/module from a file."""
    check_hash(module_file)

    graph = models.get(module_file)
    if graph:
        print(f"Loaded cached module for {module_file}")
        return graph

    with tempfile.TemporaryDirectory() as tmp_dir:
        if module_file.startswith("oci://"):
            if not ENABLE_OBJECT_STORAGE_MODULE:
                raise ModuleNotFoundError(
                    "Loading module from object storage is disabled."
                )
            print(f"Loading from object storage: {module_file}")
            basename = os.path.basename(module_file)
            fs = fsspec.filesystem("oci")
            fs.invalidate_cache()
            filename = os.path.join(tmp_dir, basename)
            fs.get_file(module_file, filename)
            hash_map[module_file] = fs.ukey(module_file)
        else:
            filename = module_file
        print(f"Importing module from {filename}")
        graph = import_from_path(os.path.join(os.path.dirname(__file__), filename))
    models[module_file] = graph
    return graph


def invoke(model: Any, inputs: Any, output_uri: Optional[str] = None) -> dict:
    """Invokes the model/module with the inputs.

    Parameters
    ----------
    model :
        A module containing an invoke() function or an object with invoke() method.
    inputs : Any
        The inputs for the invoke() call.
    output_uri : str, optional
        _description_, by default None

    Returns
    -------
    _type_
        _description_
    """
    try:
        outputs = model.invoke(inputs)
        error = None
        trace = None
    except Exception as ex:
        outputs = None
        error = str(ex)
        trace = traceback.format_exc()

    data = {"outputs": outputs, "error": error, "traceback": trace}

    if output_uri:
        print(f"Saving results to {output_uri}")
        with fsspec.open(output_uri, mode="w", encoding="utf-8") as f:
            json.dump(data, f)
        print(f"Results saved to {output_uri}")
    return data


def predict(data: Union[bytes, dict], model: Any = load_model()) -> dict:
    """Returns prediction given the model and input data."""
    # Load the data from bytes into JSON dict
    if isinstance(data, bytes):
        try:
            data = json.loads(data.decode())
        except Exception as ex:
            print(f"Data is not a valid JSON: {str(ex)}")

    if isinstance(data, dict):
        # For debugging purpose,
        # if module is specified in the data, try to reload it.
        if "module" in data:
            try:
                model = load_model(module_file=data["module"])
            except Exception as ex:
                return {
                    "outputs": None,
                    "error": str(ex),
                    "traceback": traceback.format_exc(),
                }
        inputs = data.get("inputs")
        invoke_async = data.get("async")
        invoke_id = data.get("id")
    else:
        # Pass the data as it to invoke() if it is not a dict.
        inputs = data
        invoke_async = None
        invoke_id = None

    if not invoke_id:
        invoke_id = str(uuid.uuid4())

    print(f"Invoking with inputs: {str(inputs)}")
    print(f"Invoke ID: {invoke_id}")
    if invoke_async:
        if not invoke_async.startswith("oci://"):
            return {
                "outputs": None,
                "error": "The async parameter must be a valid oci:// location.",
                "traceback": None,
            }

        output_location = os.path.join(invoke_async, f"{invoke_id}.json")
        thread = Thread(target=invoke, args=(model, inputs, output_location))
        thread.start()
        return {"id": invoke_id, "outputs": output_location}
    results = invoke(model, inputs)
    results["id"] = invoke_id
    return results
