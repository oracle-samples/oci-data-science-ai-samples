# Oracle Cloud Infrastructure Data Science and AI services Examples

The Oracle Cloud Infrastructure (OCI) Data Science service has created this repo to make demos, tutorials, and code examples that highlight various features of the [OCI Data Science service](https://www.oracle.com/data-science/cloud-infrastructure-data-science.html) and AI services. We welcome your feedback and would like to know what content is useful and what content is missing. Open an [issue](https://github.com/oracle/oci-data-science-ai-samples/issues) to do this. We know that a lot of you are creating great content and we would like to help you share it. See the [contributions](CONTRIBUTING.md) document.

Oracle Cloud Infrastructure (OCI) Data Science Services provide a powerful suite of tools for data scientists, enabling faster machine learning model development and deployment. With features like the Accelerated Data Science (ADS) SDK, distributed training, batch processing and machine learning pipelines, OCI Data Science Services offer the scalability and flexibility needed to tackle complex data science and machine learning challenges. Whether you're a beginner or an experienced machine learning practitioner or data scientist, OCI Data Science Services provide the resources you need to build, train, and deploy your models with ease.

## Topics

### [Notebook Examples](./notebook_examples/)

The [Accelerated Data Science (ADS) SDK](https://docs.oracle.com/en-us/iaas/tools/ads-sdk/latest/index.html) is a data scientist-friendly library that speeds up common data science tasks and provides an interface to other OCI services. In this section, we provide JupyterLab notebooks that offer tutorials on how to use ADS. For example, the [vault.ipynb](./ads_notebooks/vault.ipynb) notebook demonstrates how easy it is to store your secrets in the [OCI Vault service](https://docs.oracle.com/en-us/iaas/Content/KeyManagement/Concepts/keyoverview.htm).

### [Conda Environment Notebooks](./conda_environment_notebooks/)

The [OCI Data Science service](https://www.oracle.com/data-science/cloud-infrastructure-data-science.html) uses [conda environments](https://docs.conda.io/projects/conda/en/latest/index.html) to manage available libraries that a notebook can use. OCI Data Science provides several conda environments designed to offer the best libraries for common data science tasks. Each family of conda environments has notebooks that demonstrate how to perform various data science tasks. This section is organized around these conda environment families and provides notebooks to help you get started quickly.

### [Labs](./labs/)

This section provides examples of how to train machine learning models and deploy them on the OCI Data Science service, making it ideal for anyone looking to walk through an end-to-end problem.

### [Large Language Models](LLM)
OCI Data Science supports LLMs in several ways:
* Fine-tune, deploy and evaluate without writing code via [AI Quick Actions](https://docs.oracle.com/en-us/iaas/data-science/using/ai-quick-actions.htm)
* LangChain integration via [ADS](https://accelerated-data-science.readthedocs.io/en/latest/user_guide/model_registration/large_language_model.html)
* Directly by coding Python in the service. You can find more information [here](LLM)

### [Model Catalog Examples](model_catalog_examples/)

The [Model Catalog](https://docs.oracle.com/en-us/iaas/tools/ads-sdk/latest/user_guide/modelcatalog/modelcatalog.html) offers a managed and centralized storage space for models. ADS helps you create the artifacts you need to use this service. However, you must provide a [`score.py`](https://docs.oracle.com/en-us/iaas/data-science/using/model_score_py.htm) file that loads the model and a function that makes predictions. The [`runtime.yaml`](https://docs.oracle.com/en-us/iaas/data-science/using/model_runtime_yaml.htm) provides information about the runtime conda environment if you want to deploy the model. You can also document a comprehensive set of metadata about the provenance of the model. This section provides examples of how to create your `score.py` and `runtime.yaml` files for various common machine learning models and configurations.

### [Jobs](jobs/)

Oracle Cloud Infrastructure (OCI) [Data Science Jobs](https://docs.oracle.com/en-us/iaas/data-science/using/jobs-about.htm) is a powerful tool that allows you to define and run repeatable machine learning tasks on a fully managed infrastructure. With Jobs, you have the flexibility to apply custom tasks to meet your specific use cases, such as data preparation, model training, hyperparameter optimization, batch inference, large model training and more.

On-demand jobs and batch processing are especially important for businesses that need to process large volumes of data on a regular basis, as they enable companies to automate data processing workflows, reduce the need for manual intervention, and save costs associated with running compute resources for extended periods of time. With the ability to define and schedule jobs to run at specific times, businesses can automate their data processing workflows and reduce the need for manual intervention. This helps to improve efficiency, reduce errors, and save valuable time and resources. Additionally, by using a fully managed infrastructure, businesses can ensure that their data processing workflows are secure and compliant with industry regulations. Overall, OCI Data Science Jobs is a powerful tool that can help businesses to scale their machine learning workflows and improve their data processing capabilities.

### [Distributed Training](distributed_training/)

Distributed training support with Jobs for machine learning for faster and more efficient model training on large datasets, allowing for more complex models and larger workloads to be handled. Distributed training could be used when the size of the dataset or the complexity of the model makes it difficult or impossible to train on a single machine, and when there is a need for faster model training to keep up with changing data or business requirements. This section describes our support for distributed training with Jobs for the following frameworks: Dask, Horovod, TensorFlow Distributed, and PyTorch Distributed.

### [Pipelines](pipelines/)

Pipelines are essential for complex machine learning and data science tasks as they streamline and automate the model building and deployment process, enabling faster and more consistent results. They could be used when there is a need to build, train, and deploy complex models with multiple components and steps, and when there is a need to automate the machine learning process to reduce manual labor and errors. The Oracle Cloud Infrastructure [Data Science Pipelines](https://docs.oracle.com/en-us/iaas/data-science/using/pipelines-about.htm) services helps automates and streamlines the process of building and deploying machine learning pipelines.

### [ML Applications](ml-applications/)

[ML Applications](https://docs.oracle.com/en-us/iaas/data-science/using/ml-apps-about.htm) is a self-contained representation of ML use cases in Data Science. It delivers a robust MLOps platform for AI/ML delivery. It standardizes the packaging and deployment of AI/ML functionality, enabling you to build, deploy, and operate machine learning as a service. With ML Applications, you can leverage Data Science to implement AI/ML use cases and provision them into production for your applications or customers. By shortening the development lifecycle from months to weeks, ML Applications quickens the time to market while reducing operational complexity and total cost of ownership. It provides an end-to-end platform for deploying, validating, and promoting ML solutions through every stage - from development and QA to preproduction and production.

### [Data Labeling Examples](data_labeling_examples/)

The [data labeling service](https://docs.oracle.com/en-us/iaas/data-labeling/data-labeling/using/home.htm) helps identify properties (labels) of documents, text, and images (records) and annotates (labels) them with those properties. This section contains Python and Java scripts to annotate bulk numbers of records in OCI Data Labeling Service (DLS).

### [Notebook Lifecycle Script Examples](notebook_lifecycle_scripts_examples/)

The [OCI Data Science service](https://www.oracle.com/data-science/cloud-infrastructure-data-science.html) offers managed notebook(jupyterlab) sessions. Notebook lifecycle script features execute the customer provided scripts during CREATE/ACTIVATE/DEACTIVATE/DELETE notebook session lifecycle. This folder contains the examples script which needs little to no editing and ready to be used as lifecycle scripts input.

### [Feature Store](./feature_store/)

The [Feature store service](https://feature-store-accelerated-data-science.readthedocs.io/en/latest/) solves many of the problems because it is a centralized way to transform and access data for training and serving time, Feature stores help define a standardised pipeline for ingestion of data and querying of data.

## Documentation

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

## Need Help?

* Create a GitHub [issue](https://github.com/oracle/oci-data-science-ai-samples/issues).

## Contributing

This project welcomes contributions from the community. Before submitting a pull request, please [review our contribution guide](./CONTRIBUTING.md).

## Security

The [Security Guide](./SECURITY.md) contains information about security vulnerability disclosure process. If you discover a vulnerability, consider filing an [issue](https://github.com/oracle/oci-data-science-ai-samples/issues).

## License

Copyright (c) 2021, 2023 Oracle and/or its affiliates.

Released under the Universal Permissive License v1.0 as shown at
<https://oss.oracle.com/licenses/upl/>.
