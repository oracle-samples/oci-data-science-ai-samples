Oracle Cloud Infrastructure Data Science and AI services Examples
=================================================================

The Oracle Cloud Infrastructure (OCI) Data Science service has created this repo to make demos, tutorials, and code examples that highlight various features of the [OCI Data Science service](https://www.oracle.com/data-science/cloud-infrastructure-data-science.html) and AI services. We welcome your feedback and would like to know what content is useful and what content is missing. Open an [issue](https://github.com/oracle/oci-data-science-ai-samples/issues) to do this. We know that a lot of you are creating great content and we would like to help you share it. See the [contributions](CONTRIBUTING.md) document.

# Sections

* [notebook_examples](./notebook_examples/): The [Accelerated Data Science (ADS) SDK](https://docs.oracle.com/en-us/iaas/tools/ads-sdk/latest/index.html) is a data scientist friendly library that helps you speed up common data science tasks and it also provides an interface to other OCI services. This section contains JupyterLab notebooks that provide tutorials on how to use ADS. For example, the [vault.ipynb](./ads_notebooks/vault.ipynb) shows how easy it is to store you secrets in the [OCI Vault service](https://docs.oracle.com/en-us/iaas/Content/KeyManagement/Concepts/keyoverview.htm).
&nbsp;
* [conda_environment_notebooks](./conda_environment_notebooks/): The [OCI Data Science service](https://www.oracle.com/data-science/cloud-infrastructure-data-science.html) uses [conda environments](https://docs.conda.io/projects/conda/en/latest/index.html) to manage the available libraries that a notebook can use. OCI The Data Science service [provides a number of conda environments](https://docs.oracle.com/en-us/iaas/data-science/using/conda_understand_environments.htm) that are designed to give you the best in class libraries for common data science tasks. Each family of conda environments has notebooks that demonstrate how to perform different data science tasks. This section is organized around these conda environment families and provides the notebooks that you need to get you started quickly.
&nbsp;
* [knowledge_base](./knowledge_base/): Are you struggling with a problem? Check out the knowledge base. It has a growing section of articles on how to solve common problems that you may encounter. If you have had a problem and have solved it, please consider [contributing](./CONTRIBUTING.md) your solution. If you had a problem, others probably have had the same one.
&nbsp;
* [labs](./labs/): Looking to walk through an end-to-end problem? Check out this section. It has examples of how to train machine learning models and then deploy them on the OCI Data Science service. Have you built an end-to-end machine learning model and want to share it with others. Please consider [contributing](./CONTRIBUTING.md) it.
&nbsp;
* [model_catalog_examples](model_catalog_examples/): The [model catalog](https://docs.oracle.com/en-us/iaas/tools/ads-sdk/latest/user_guide/modelcatalog/modelcatalog.html) provides a managed and centralized storage space for models. ADS helps you create the artifacts that you need to use this service. However, you need to provide a [`score.py`](https://docs.oracle.com/en-us/iaas/data-science/using/model_score_py.htm) file that will load the model and a function that will make predictions. The [`runtime.yaml`](https://docs.oracle.com/en-us/iaas/data-science/using/model_runtime_yaml.htm) provides information about the runtime conda environment if you want to deploy the model. It also allows you to document a comprehensive set of metadata about the provenance of the model. The section of the repo provides examples of how to create your `score.py` and `runtime.yaml` files for various common machine learning models. There are many different models and configurations. If you have developed a machine learning model that is not in this section, please consider [contributing](./CONTRIBUTING.md) it.
&nbsp;
* [jobs](jobs/): Jobs enables you to define and run a repeatable machine learning task on a fully managed infrastructure. Jobs enable custom tasks, so you can apply any use case you may have such as data preparation, model training, hyperparameter optimization, batch inference and so on.
&nbsp;
* [distributed training](distributed_training/): support for distributed training with Jobs for the frameworks: Dask, Horovod, TensorFlow Distributed and PyTorch Distributed.
&nbsp;
* [data_labeling_examples](data_labeling_examples/): The [data labeling service](https://docs.oracle.com/en-us/iaas/data-labeling/data-labeling/using/home.htm) helps in the process of identifying properties (labels) of documents, text, and images (records), and annotating (labeling) them with those properties. This sections contains Python and Java scripts to annotate bulk number of records in OCI Data Labeling Service (DLS). If you have developed some functionality over/for dls, that you would like to share, please consider [contributing](./CONTRIBUTING.md) it.

# Resources

Check out the following resources for more information about the OCI Data Science and AI services:

* [ADS class documentation](https://accelerated-data-science.readthedocs.io/en/latest/modules.html)
* [ADS user guide](https://accelerated-data-science.readthedocs.io/en/latest/index.html)
* [AI & Data Science blog](https://blogs.oracle.com/ai-and-datascience/)
* [OCI Data Science service guide](https://docs.oracle.com/en-us/iaas/data-science/using/data-science.htm)
* [OCI Data Science service release notes](https://docs.cloud.oracle.com/en-us/iaas/releasenotes/services/data-science/)
* [YouTube playlist](https://www.youtube.com/playlist?list=PLKCk3OyNwIzv6CWMhvqSB_8MLJIZdO80L)
* [OCI Data Labeling Service guide](https://docs.oracle.com/en-us/iaas/data-labeling/data-labeling/using/home.htm)
* [OCI DLS DP API](https://docs.oracle.com/en-us/iaas/api/#/en/datalabeling-dp/20211001/)
* [OCI DLS CP API](https://docs.oracle.com/en-us/iaas/api/#/en/datalabeling/20211001/)

# Need Help?

* Create a GitHub [issue](https://github.com/oracle/oci-data-science-ai-samples/issues).

# Contributing

This project welcomes contributions from the community. Before submitting a pull request, please [review our contribution guide](./CONTRIBUTING.md).

## Security

The [Security Guide](./SECURITY.md) contains information about security vulnerability disclosure process. If you discover a vulnerability, consider filing an [issue](https://github.com/oracle/oci-data-science-ai-samples/issues).
