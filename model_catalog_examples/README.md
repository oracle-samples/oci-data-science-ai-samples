## Model Catalog Examples

* In this directory we have several examples of runtime.yaml and score.py files that can be used to deploy models. There is a wide range of kinds of models including NLP, PyTorch, XGBoost and LighGBM.

* We also have [example notebooks](./notebook_examples/) which serve as tutorials to prepare and save different model artifacts and then deploy them as well.

* It also contains [boilerplate code](./artifact_boilerplate) to generate the model artifact. We have provided template score.py and runtime.yaml which user can use and define them accordingly.
* We also have a [tool](./artifact_boilerplate/artifact_introspection_test) to run the model introspection tests. 
    - These tests run a series of introspection tests on the model artifact before saving the model to the model catalog. The purpose of these tests is to capture many of the common model artifact errors before the model is saved to the model catalog. 
    - Introspection tests check `score.py` for syntax errors, verify the signature of functions `load_model()` and `predict()`, and validate the content of `runtime.yaml`. 
    - The introspection tests are present in [model_artifact_validate.py](./artifact_boilerplate/artifact_introspection_test/model_artifact_validate.py). More details are present in [README.md](./artifact_boilerplate/README.md).
