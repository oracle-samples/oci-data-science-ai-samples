# Model Artifact Boilerplate Code

This directory contains boilerplate code to generate a model artifact.

The artifact should minimally contain the following files:
- score.py
- runtime.yaml

Follow the steps below to successfully create a model artifact.

## Step 1. Save Your Model Object

You can use a variety of tools to save your model (joblib, cloudpickle, pickle, onnx, etc). We recommend that you save your model
object in the top level directory of your model artifact, at the same level as `score.py` and `runtime.yaml`.

## Step 2. Modify `score.py`

Two functions are defined in score.py: `load_model()` and `predict()`. You will need to customize the body of the both functions to support your model.

* `load_model()` reads the model file on disk and returns the estimator object. When modifying `load_model()`, **make sure that you use the same library for serializing
and de-serializing the model object**.

* `predict()` has two parameters: `data` and `model`. The required parameter is `data` which represents a dataset payload while `model` is an optional parameter.
  By default `model` is the object returned by `load_model()`. Ensure that the data type of the `data` parameter matches the payload format you expect with model deployment.
  By default, Model Deployment assumes that `data` is a JSON payload (application/json). The `predict()` function should be able to convert the JSON payload into, for example,  a Pandas Dataframe or a Numpy array
  if that is the data format supported by the the model object. In addition, the body of predict() can include data transformations and other data manipulation tasks before a model prediction is made.

A few additional things to keep in mind:

* The function signatures of `load_model()` and `predict()`, are not editable. Only the body of these functions is customizable.

* any custom Python modules can be imported in score.py if they are available in the artifact file or as part of the conda environment used for inference purposes.

* You can save more than one model object in your artifact and load more than one estimator object to memory to perform an ensemble evaluation.
  In this case, `load_model()` could return an array of model objects that are processed by `predict()`


## (OPTIONAL) Step 3. Test the score.predict() Function

We recommend that you test the `predict()` function in your local environment before saving the model to the catalog. The code snippet below
showcases how you can pass a json payload to predict that would mimic the behavior of your model as deployed through Model Deployment. This is a good
way to check that the model object is read by `load_model()` and that the predictions returned by your models are correct and in the format you expect.

```
import sys
from json import dumps

# The local path to your model artifact directory is added to the Python path.
# replace <your-model-artifact-path>
sys.path.insert(0, f"<your-model-artifact-path>")

# importing load_model() and predict() that are defined in score.py
from score import load_model, predict

# Loading the model to memory
_ = load_model()
# Making predictions on a JSON string object (dumps(data)). Here we assume
# that predict() is taking data in JSON format
predictions_test = predict(dumps(data), _)
predictions_test
```

## Step 4. Modify runtime.yaml

Next, modify the runtime.yaml file. This file provides a reference to the conda environment you want to use for the runtime environment for Model Deployment.
Minimally `runtime.yaml` should contain the following fields:

```
MODEL_ARTIFACT_VERSION: '3.0'
MODEL_DEPLOYMENT:
  INFERENCE_CONDA_ENV:
    INFERENCE_ENV_PATH: <conda-environment-path-on-object-storage> # For example: "oci://service_conda_packs@ociodscdev/service_pack/cpu/General Machine Learning for CPUs/1.0/mlcpuv1"
    INFERENCE_PYTHON_VERSION: '3.7' #
```

Go to this page [link](https://docs.oracle.com/en-us/iaas/data-science/using/model_runtime_yaml.htm) for a definition of all the parameters that can be included in `runtime.yaml`.  

As an example, here's a complete `runtime.yaml` for a data_science conda environment (mlcpuv1) used as a runtime environment for model deployment.
In most cases the runtime environment for model deployment should be the same as the conda environment used to train the model.

```
MODEL_ARTIFACT_VERSION: '3.0'
MODEL_DEPLOYMENT:
  INFERENCE_CONDA_ENV:
    INFERENCE_ENV_PATH: oci://service-conda-packs@id19sfcrra6z/service_pack/cpu/General
      Machine Learning for CPUs/1.0/mlcpuv1
    INFERENCE_PYTHON_VERSION: 3.6.11
```

## (OPTIONAL) Step 5. Provide Model Input and Output Data Schema

Next, you can optionally include a data schema definition for both the input feature vector of your model as well as a schema describing the predictions returned by your model.
It is possible to add these schemas after the model has been saved to the catalog.


## (OPTIONAL) Step 6. Run Model Artifact Introspection Tests

Next, run a series of introspection tests on your model artifact before saving the model to the model catalog. The purpose of these tests is to capture many of the
common model artifact errors before the model is saved to the model catalog. Introspection tests check `score.py` for syntax errors, verify the signature of
functions `load_model()` and `predict()`, and validate the content of `runtime.yaml`. The introspection tests are found in `model-artifact-validation/model_artifact_validate.py`.

### Introspection on a previously created artifact

Perhaps you already have a model artifact in your notebook session or your local laptop and you would like to execute the introspection tests on that artifact. It is possible to execute the introspection tests on a **previously created artifact**.  Simply copy the entire directory `artifact_introspection_test` into the top level directory of your model artifact and follow the steps below.


### Required files
```
artifact_introspection_test/requirements.txt
artifact_introspection_test/index.json
artifact_introspection_test/model_artifact_validate.py
```

### Installation

Python version > 3.5 is required to run the tests. Before running the tests locally on your machine, two Python libraries need to be installed
namely `pyyaml` and `requests`. This installation step is a one-time operation. Go to your artifact directory and run the following command:

```
python3 -m pip install --user -r artifact_introspection_test/requirements.txt
```

### Running the Tests Locally

Next, replace `<artifact-path>` with the path to your model artifact directory
```
python3 artifact_introspection_test/model_artifact_validate.py --artifact <artifact-path>
```

The script automatically generates a report of the test results in the same folder . Two files are generated containing the test results in different formats:  
* `test_json_output.json`
* `test_html_output.html`

Repeat Steps 1-6 until no error is found.


## Step 7. Create/Save your model to the catalog

The following section describes the SDK access through OCI configuration file which is part of standard SDK access management.

#### Initialize Client
```
# Create a default config using DEFAULT profile in default location
# Refer to
# https://docs.cloud.oracle.com/en-us/iaas/Content/API/Concepts/sdkconfig.htm#SDK_and_CLI_Configuration_File
# for more info

import oci
from oci.data_science.models import CreateModelDetails, Metadata, CreateModelProvenanceDetails, UpdateModelDetails, UpdateModelProvenanceDetails
config = oci.config.from_file()
data_science_client = oci.data_science.DataScienceClient(config=config)

# Initialize service client with user principal (config file)
config = oci.config.from_file()
data_science_client = oci.data_science.DataScienceClient(config=config)

# Alternatively initialize service client with resource principal (for example in a notebook session)
# auth = oci.auth.signers.get_resource_principals_signer()
# data_science_client = oci.data_science.DataScienceClient({}, signer=auth)
```

## Step 7.1 (OPTIONAL) Step 7.1 Document the Model Provenance

You can first document the model provenance. This is optional. The table below includes a list of the supported model provenance metadata
* When you save a model to the catalog with ADS, ADS automatically captures all provenance metadata values.

|             |                                                               |
| ----------- | ------------------------------------------------------------  |
| Field/Key      | Description                                                        |
| repository_url | URL of the remote git repository |
| git_branch    | Branch of the git repo |
| git_commit |   Commit ID |
| script_dir |  Local path to the artifact directory |
|training_id | OCID of the resource (Notebook Session, Job Run) used to train the model. |
| | Note that the environment variables: |
|   |   * NB_SESSION_OCID |
|   |   * JOB_RUN_OCID |
|   |   Are available for you to use and refer to when you save a model with the OCI SDK. |

An example code snippet:

MODEL PROVENANCE METADATA

```
provenance_details = CreateModelProvenanceDetails(repository_url="EXAMPLE-repositoryUrl-Value",
                                                  git_branch="EXAMPLE-gitBranch-Value",
                                                  git_commit="EXAMPLE-gitCommit-Value",
                                                  script_dir="EXAMPLE-scriptDir-Value",
                                                  # OCID of the ML job Run or Notebook session on which this model was
                                                  # trained
                                                  training_id="<<Notebooksession or ML Job Run OCID>>"
                                                  )
```
## (OPTIONAL) Step 7.2: Document Model Taxonomy


The metadata fields associated with model taxonomy allow you to describe the machine learning use case and framework behind the model.  The defined metadata tags are the list of allowed values for use case type and framework for defined metadata and category values for custom metadata.
* When you save a model to the catalog with ADS, ADS automatically captures all model taxonomy metadata values.

|             |                                                               |
| ----------- | ------------------------------------------------------------  |
| Field/Key      | Description                                                        |
| UseCaseType | Describes the machine learning use case associated with the model. You select one of the following allowed values: |
|     | binary_classification |
|  |   regression |
|  |   multinomial_classification |
|  |   clustering |
|  |   recommender |
|  |   dimensionality_reduction/representation |
|  |   time_series_forecasting |
|  |   anomaly_detection |
|  |   topic_modeling |
|  |   ner |
|  |   sentiment_analysis |
|  |   image_classification |
|  |   object_localization |
|  |   other |
| Framework |   The machine learning framework associated with the model. You select one of the following allowed values: |
|  |   scikit-learn |
|  |   xgboost |
|  |   tensorflow |
|  |   pytorch |
|  |   mxnet |
|  |   keras |
|  |   lightGBM |
|  |   pymc3 |
|  |   pyOD |
|  |   spacy |
|  |   prophet |
|  |   sktime |
|  |   statsmodels |
|  |   cuml |
|  |   oracle_automl |
|  |   h2o |
|  |   transformers |
|  |   nltk |
|  |   emcee |
|  |   pystan |
|  |   bert |
|  |   gensim |
|  |   flair |
|  |   word2vec |
|  |   ensemble (more than one library) |
|  |   other |
| FrameworkVersion |   The machine learning framework version. This is a free text value.  |
| Algorithm |   The algorithm or model instance class. This is a free text value.  |
| Hyperparameters |   The hyperparameters of the model object. This should be a JSON blob.  |
| ArtifactTestResults |   The JSON output of the artifact tests run on the client side. See (OPTIONAL) Step 7.5 - Document the Introspection Tests Results below. |

Here's a code snippet showing how you can document the model taxonomy. Capture each key-value pair by creating a list of Metadata() objects:

MODEL TAXONOMY METADATA

```
# create the list of defined metadata around model taxonomy:
defined_metadata_list = [
    Metadata(key="UseCaseType", value="image_classification"),
    Metadata(key="Framework", value="keras"),
    Metadata(key="FrameworkVersion", value="0.2.0"),
    Metadata(key="Algorithm",value="ResNet"),
    Metadata(key="hyperparameters",value="{\"max_depth\":\"5\",\"learning_rate\":\"0.08\",\"objective\":\"gradient descent\"}")
]
```

## (OPTIONAL) Step 7.3: Add Your Own Custom Metadata

You can add your own custom metadata to document your model. The code snippet shows how you can add custom metadata to capture the model accuracy, the environment , and the source of the training data:
* The max allowed size for all metadata (combined Defined + Custom) is 32 kb

Each custom metadata has four attributes:

```
Atribute   |  Required/Optional |  Description
key        |  Required          |  The key/label of your custom metadata
value      |  Required          |  The value attached to the key
category   |  Optional          |  The category of the metadata. Select one of these five values:
                                    1. Performance
                                    2. Training Profile
                                    3. Training and Validation Datasets
                                    4. Training Environment
                                    5. other

                                   The category attribute is useful to filter custom metadata. This becomes handy when one has a large number of custom metadata for a given model.                                 

description | Optional           | A description of the custom medata.

```


ADDING CUSTOM METADATA
```
# Adding your own custom metadata:
custom_metadata_list = [
    Metadata(key="Image Accuracy Limit", value="70-90%", category="Performance",
             description="Performance accuracy accepted"),
    Metadata(key="Pre-trained environment",
             value="https://blog.floydhub.com/guide-to-hyperparameters-search-for-deep-learning-models/",
             category="Training environment", description="Environment link for pre-trained model"),
    Metadata(key="Image Sourcing", value="https://lionbridge.ai/services/image-data/", category="other",
             description="Source for image training data")
]
```
## (Optional) Step 7.4: Document the Model Input and Output Data Schema Definitions

Next, you can document the model input and output data schemas. For more details on the format of the schema definition
* When you save a model to the catalog with ADS, ADS automatically captures the model input and output data schema definitions.
* The max allowed size for schemas (combined Input and Output) is 32 kb

DOCUMENT MODEL INPUT AND OUTPUT SCHEMAS

```
import json
from json import load
# Declare input/output schema for our model - this is optional
# It must be a valid json or yaml string
# Schema like model artifact is immutable hence it is allowed only at the model creation time and cannot be updated
# Schema json sample in appendix
input_schema = load(open('SR_input_schema.json','rb'))
input_schema_str= json.dumps(input_schema)
output_schema = load(open('SR_output_schema.json','rb'))
output_schema_str= json.dumps(output_schema)
```
## (Optional) Step 7.5: Document the Introspection Test Results

This is the results output from step 5 which can be uploaded as a defined metadata key "ArtifactTestResults" with the value of execution output. This is an important step if you wish to see the result in console as "Model Introspection" for future reference and traceability.

DOCUMENT MODEL INPUT AND OUTPUT SCHEMAS
```
# Provide the introspection test results

test_results = load(open('test_json_output.json','rb'))
test_results_str = json.dumps(test_results)
defined_metadata_list.extend([Metadata(key="ArtifactTestResults", value=test_results_str)])
```

## Step 7.6: Wrapping it All: Creating/Saving the Model in the Model Catalog

Last we create the model in the model catalog.

CREATE MODEL

```
# creating a model details object:
model_details = CreateModelDetails(
    compartment_id='<compartment-ocid-of-model>',
    project_id='<project-ocid>',
    display_name='<display-name-of-model>',
    description='<description-of-model>',
    custom_metadata_list=custom_metadata_list,
    defined_metadata_list=defined_metadata_list,
    input_schema=input_schema_str,
    output_schema=output_schema_str)

# creating the model object:
model = data_science_client.create_model(model_details)
# adding the provenance:
data_science_client.create_model_provenance(model.data.id, provenance_details)
# adding the artifact:
with open('<path-to-artifact-zip-archive>','rb') as artifact_file:
    artifact_bytes = artifact_file.read()
    data_science_client.create_model_artifact(model.data.id, artifact_bytes, content_disposition='attachment; filename="{model.data.id}.zip"')
```
Once a model is created you can view it in the console

---

# Appendix

## Artifact introspection tests

```
#   Test Key            Test Name
1   score_py            Check that the file "score.py" exists and is in the top level directory of the artifact directory
2   runtime_yaml        Check that the file "runtime.yaml" exists and is in the top level directory of the artifact directory
3   score_syntax        Check for Python syntax errors
4   score_load_model    Check that load_model() is defined
5   score_predict       Check that predict() is defined
6   score_predict_data  Check that the only required argument for predict() is named "data"
7   score_predict_arg   Check that all other arguments in predict() are optional and have default values
8   runtime_version     Check that field MODEL_ARTIFACT_VERSION is set to 3.0
9   runtime_env_python  Check that field MODEL_DEPLOYMENT.INFERENCE_PYTHON_VERSION is set to a value of 3.6 or higher
10  runtime_env_path    Check that field MODEL_DEPLOYMENT.INFERENCE_ENV_PATH is set
11  runtime_path_exist  Check that the file path in MODEL_DEPLOYMENT.INFERENCE_ENV_PATH is correct
```
