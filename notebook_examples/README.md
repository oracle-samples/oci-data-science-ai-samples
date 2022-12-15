
ADS Expertise Notebooks
=======================

The [Accelerated Data Science (ADS) SDK](https://accelerated-data-science.readthedocs.io/en/latest/) is maintained by the Oracle Cloud Infrastructure Data Science service team. It speeds up common data science activities by providing tools that automate and/or simplify common data science tasks, along with providing a data scientist friendly pythonic interface to Oracle Cloud Infrastructure (OCI) services, most notably OCI Data Science, Data Flow, Object Storage, and the Autonomous Database. ADS gives you an interface to manage the lifecycle of machine learning models, from data acquisition to model evaluation, interpretation, and model deployment.

The ADS SDK can be downloaded from [PyPi](https://pypi.org/project/oracle-ads/), contributions welcome on [GitHub](https://github.com/oracle/accelerated-data-science)

    


## Topics
<img src="https://img.shields.io/badge/deploy model-6-brightgreen"> <img src="https://img.shields.io/badge/register model-6-brightgreen"> <img src="https://img.shields.io/badge/train model-6-brightgreen"> <img src="https://img.shields.io/badge/data flow-4-brightgreen"> <img src="https://img.shields.io/badge/pyspark-4-brightgreen"> <img src="https://img.shields.io/badge/oracle open data-3-brightgreen"> <img src="https://img.shields.io/badge/bds-3-brightgreen"> <img src="https://img.shields.io/badge/xgboost-2-brightgreen"> <img src="https://img.shields.io/badge/data catalog metastore-2-brightgreen"> <img src="https://img.shields.io/badge/nlp-2-brightgreen"> <img src="https://img.shields.io/badge/big data service-2-brightgreen"> <img src="https://img.shields.io/badge/scikit learn-2-brightgreen"> <img src="https://img.shields.io/badge/autonomous driving-1-brightgreen"> <img src="https://img.shields.io/badge/tensorflow-1-brightgreen"> <img src="https://img.shields.io/badge/authentication-1-brightgreen"> <img src="https://img.shields.io/badge/api keys-1-brightgreen"> <img src="https://img.shields.io/badge/iam-1-brightgreen"> <img src="https://img.shields.io/badge/access management-1-brightgreen"> <img src="https://img.shields.io/badge/caltech-1-brightgreen"> <img src="https://img.shields.io/badge/pedestrian detection-1-brightgreen"> <img src="https://img.shields.io/badge/dcat-1-brightgreen"> <img src="https://img.shields.io/badge/pytorch-1-brightgreen"> <img src="https://img.shields.io/badge/model evaluation-1-brightgreen"> <img src="https://img.shields.io/badge/binary classification-1-brightgreen"> <img src="https://img.shields.io/badge/regression-1-brightgreen"> 

## Notebooks
### - API Keys
#### [`api_keys-authentication.ipynb`](api_keys-authentication.ipynb)

 
Configure and test API key authentication, attach keys to user account through Oracle's identity service, and test access to the API.

This notebook was developed on the conda pack with slug: *generalml\_p37\_cpu\_v1*

 
`authentication`  `api keys`  `iam`  `access management`

<sub>Universal Permissive License v 1.0</sup>

---
### - Audi Autonomous Driving Dataset Repository
#### [`audi-autonomous_driving-oracle_open_data.ipynb`](audi-autonomous_driving-oracle_open_data.ipynb)

 
Download, process and display autonomous driving data, and map LiDAR data onto images.

This notebook was developed on the conda pack with slug: *computervision\_p37\_cpu\_v1*

 
`autonomous driving`  `oracle open data`

<sub>Universal Permissive License v 1.0</sup>

---
### - How to Read Data with fsspec from Oracle Big Data Service (BDS)
#### [`read-write-big_data_service-(BDS).ipynb`](read-write-big_data_service-(BDS).ipynb)

 
Manage data using fsspec file system. Read and save data using pandas and pyarrow through fsspec file system.

This notebook was developed on the conda pack with slug: *pyspark30\_p37\_cpu\_v5*

 
`bds`  `fsspec`

<sub>Universal Permissive License v 1.0</sup>

---
### - Using Livy on the Big Data Service
#### [`big_data_service-(BDS)-livy.ipynb`](big_data_service-(BDS)-livy.ipynb)

 
Work interactively with a BDS cluster using Livy and two different connection techniques, SparkMagic (for a notebook environment) and with REST.

This notebook was developed on the conda pack with slug: *pyspark30\_p37\_cpu\_v5*

 
`bds`  `big data service`  `livy`

<sub>Universal Permissive License v 1.0</sup>

---
### - Caltech Pedestrian Detection Benchmark Repository
#### [`caltech-pedestrian_detection-oracle_open_data.ipynb`](caltech-pedestrian_detection-oracle_open_data.ipynb)

 
Download and process annotated video data of vehicles and pedestrians.

This notebook was developed on the conda pack with slug: *generalml\_p37\_cpu\_v1*

 
`caltech`  `pedestrian detection`  `oracle open data`

<sub>Universal Permissive License v 1.0</sup>

---
### - Using Data Catalog Metastore with DataFlow
#### [`pyspark-data_catalog-hive_metastore-data_flow.ipynb`](pyspark-data_catalog-hive_metastore-data_flow.ipynb)

 
Write and test a Data Flow batch application using the Oracle Cloud Infrastructure (OCI) Data Catalog Metastore. Configure the job, run the application and clean up resources.

This notebook was developed on the conda pack with slug: *pyspark30\_p37\_cpu\_v5*

 
`data catalog metastore`  `data flow`

<sub>Universal Permissive License v 1.0</sup>

---
### - Text Classification with Data Labeling Service Integration
#### [`data_labeling-text_classification.ipynb`](data_labeling-text_classification.ipynb)

 
Use the Oracle Cloud Infrastructure (OCI) Data Labeling service to efficiently build enriched, labeled datasets for the purpose of accurately training AI/ML models. This notebook demonstrates operations that can be performed using the Advanced Data Science (ADS) Data Labeling module.

This notebook was developed on the conda pack with slug: *nlp\_p37\_cpu\_v2*

 
`data labeling`  `text classification`

<sub>Universal Permissive License v 1.0</sup>

---
### - Visualizing Data
#### [`visualizing_data-exploring_data.ipynb`](visualizing_data-exploring_data.ipynb)

 
Perform common data visualization tasks and explore data with the ADS SDK. Plotting approaches include 3D plots, pie chart, GIS plots, and Seaborn pairplot graphs.

This notebook was developed on the conda pack with slug: *generalml\_p37\_cpu\_v1*

 
`data visualization`  `seaborn plot`  `charts`

<sub>Universal Permissive License v 1.0</sup>

---
### - Using Data Catalog Metastore with PySpark
#### [`pyspark-data_catalog-hive_metastore.ipynb`](pyspark-data_catalog-hive_metastore.ipynb)

 
Configure and use PySpark to process data in the Oracle Cloud Infrastructure (OCI) Data Catalog metastore, including common operations like creating and loading data from the metastore.

This notebook was developed on the conda pack with slug: *pyspark30\_p37\_cpu\_v5*

 
`dcat`  `data catalog metastore`  `pyspark`

<sub>Universal Permissive License v 1.0</sup>

---
### - Train, Register, and Deploy a Generic Model
#### [`train-register-deploy-other-frameworks.ipynb`](train-register-deploy-other-frameworks.ipynb)

 
Train, register, and deploy a generic model

This notebook was developed on the conda pack with slug: *generalml\_p37\_cpu\_v1*

 
`generic model`  `deploy model`  `register model`  `train model`

<sub>Universal Permissive License v 1.0</sup>

---
### - Introduction to ADSTuner
#### [`hyperparameter_tuning.ipynb`](hyperparameter_tuning.ipynb)

 
Use ADSTuner to optimize an estimator using the scikit-learn API

This notebook was developed on the conda pack with slug: *generalml\_p37\_cpu\_v1*

 
`hyperparameter tuning`

<sub>Universal Permissive License v 1.0</sup>

---
### - Intel Extension for Scikit-Learn
#### [`accelerate-scikit_learn-with-intel_extension.ipynb`](accelerate-scikit_learn-with-intel_extension.ipynb)

 
Enhance performance of scikit-learn models using the Intel(R) oneAPI Data Analytics Library. Train a k-means model using both sklearn and the accelerated Intel library and compare performance.

This notebook was developed on the conda pack with slug: *sklearnex202130\_p37\_cpu\_v1*

 
`intel`  `intel extension`  `scikit-learn`  `scikit learn`

<sub>Universal Permissive License v 1.0</sup>

---
### - Connect to Oracle Big Data Service
#### [`big_data_service-(BDS)-kerberos.ipynb`](big_data_service-(BDS)-kerberos.ipynb)

 
Connect to Oracle Big Data services using Kerberos.

This notebook was developed on the conda pack with slug: *pyspark30\_p37\_cpu\_v5*

 
`kerberos`  `big data service`  `bds`

<sub>Universal Permissive License v 1.0</sup>

---
### - Natural Language Processing
#### [`natural_language_processing.ipynb`](natural_language_processing.ipynb)

 
Use the ADS SDK to process and manipulate strings. This notebook includes regular expression matching and natural language (NLP) parsing, including part-of-speech tagging, named entity recognition, and sentiment analysis. It also shows how to create and use custom plugins specific to your specific needs.

This notebook was developed on the conda pack with slug: *nlp\_p37\_cpu\_v2*

 
`language services`  `string manipulation`  `regex`  `regular expression`  `natural language processing`  `NLP`  `part-of-speech tagging`  `named entity recognition`  `sentiment analysis`  `custom plugins`

<sub>Universal Permissive License v 1.0</sup>

---
### - Train, Register, and Deploy a LightGBM Model
#### [`train-register-deploy-lightgbm.ipynb`](train-register-deploy-lightgbm.ipynb)

 
Train, register, and deploy a LightGBM model.

This notebook was developed on the conda pack with slug: *generalml\_p37\_cpu\_v1*

 
`lightgbm`  `deploy model`  `register model`  `train model`

<sub>Universal Permissive License v 1.0</sup>

---
### - Loading Data with DatasetFactory
#### [`load_data-object_storage-hive-autonomous-database.ipynb`](load_data-object_storage-hive-autonomous-database.ipynb)

 
Load data from a variety of sources and in different formats. Sources include local storage, OCI storage, and different databases. Formats include Pandas DataFrames, parquet, excel, csv, and Python primitives.

This notebook was developed on the conda pack with slug: *generalml\_p37\_cpu\_v1*

 
`loading data`

<sub>Universal Permissive License v 1.0</sup>

---
### - Introduction to Model Version Set
#### [`model_version_set.ipynb`](model_version_set.ipynb)

 
A model version set is a way to track the relationships between models. As a container, the model version set takes a collection of models. Those models are assigned a sequential version number based on the order they are entered into the model version set.

This notebook was developed on the conda pack with slug: *dbexp\_p38\_cpu\_v1*

 
`model`  `model experiments`  `model version set`

<sub>Universal Permissive License v 1.0</sup>

---
### - Model Evaluation with ADSEvaluator
#### [`model_evaluation-with-ADSEvaluator.ipynb`](model_evaluation-with-ADSEvaluator.ipynb)

 
Train and evaluate different types of models: binary classification using an imbalanced dataset, multi-class classification using a synthetically generated dataset consisting of three equally distributed classes, and a regression using a synthetically generated dataset with positive targets.

This notebook was developed on the conda pack with slug: *generalml\_p37\_cpu\_v1*

 
`model evaluation`  `binary classification`  `regression`  `multi-class classification`  `imbalanced dataset`  `synthetic dataset`

<sub>Universal Permissive License v 1.0</sup>

---
### - Text Classification and Model Explanations using LIME
#### [`text_classification-model_explanation-lime.ipynb`](text_classification-model_explanation-lime.ipynb)

 
Perform model explanations on an NLP classifier using the locally interpretable model explanations technique (LIME).

This notebook was developed on the conda pack with slug: *nlp\_p37\_cpu\_v2*

 
`nlp`  `lime`  `model_explanation`  `text_classification`  `text_explanation`

<sub>Universal Permissive License v 1.0</sup>

---
### - Visual Genome Repository
#### [`genome_visualization-oracle_open_data.ipynb`](genome_visualization-oracle_open_data.ipynb)

 
Load visual data, define regions, and visualize objects using metadata to connect structured images to language.

This notebook was developed on the conda pack with slug: *generalml\_p37\_cpu\_v1*

 
`object annotation`  `genome visualization`  `oracle open data`

<sub>Universal Permissive License v 1.0 (https://oss.oracle.com/licenses/upl/)</sup>

---
### - Working with Pipelines [Limited Availability]
#### [`pipelines-ml_lifecycle.ipynb`](pipelines-ml_lifecycle.ipynb)

 
Create and use ML pipelines through the entire machine learning lifecycle

This notebook was developed on the conda pack with slug: *generalml\_p37\_cpu\_v1*

 
`pipelines`  `pipeline step`  `jobs pipeline`

<sub>Universal Permissive License v 1.0</sup>

---
### - Spark NLP within Oracle Cloud Infrastructure Data Flow Studio
#### [`pyspark-data_flow_studio-spark_nlp.ipynb`](pyspark-data_flow_studio-spark_nlp.ipynb)

 
Demonstrates how to use Spark NLP within a long lasting Oracle Cloud Infrastructure Data Flow cluster.

This notebook was developed on the conda pack with slug: *pyspark32\_p38\_cpu\_v1*

 
`pyspark`  `data flow`

<sub>Universal Permissive License v 1.0</sup>

---
### - Introduction to the Oracle Cloud Infrastructure Data Flow Studio
#### [`pyspark-data_flow_studio-introduction.ipynb`](pyspark-data_flow_studio-introduction.ipynb)

 
Run interactive Spark workloads on a long lasting Oracle Cloud Infrastructure Data Flow Spark cluster through Apache Livy integration. Data Flow Spark Magic is used for interactively working with remote Spark clusters through Livy, a Spark REST server, in Jupyter notebooks. It includes a set of magic commands for interactively running Spark code.

This notebook was developed on the conda pack with slug: *pyspark32\_p38\_cpu\_v1*

 
`pyspark`  `data flow`

<sub>Universal Permissive License v 1.0</sup>

---
### - PySpark
#### [`pyspark-data_flow-application.ipynb`](pyspark-data_flow-application.ipynb)

 
Develop local PySpark applications and work with remote clusters using Data Flow.

This notebook was developed on the conda pack with slug: *pyspark24\_p37\_cpu\_v3*

 
`pyspark`  `data flow`

<sub>Universal Permissive License v 1.0</sup>

---
### - Train, Register, and Deploy a PyTorch Model
#### [`train-register-deploy-pytorch.ipynb`](train-register-deploy-pytorch.ipynb)

 
Train, register, and deploy a PyTorch model.

This notebook was developed on the conda pack with slug: *pytorch110\_p37\_cpu\_v1*

 
`pytorch`  `deploy model`  `register model`  `train model`

<sub>Universal Permissive License v 1.0</sup>

---
### - Train, register, and deploy Sklearn Model
#### [`train-register-deploy-sklearn.ipynb`](train-register-deploy-sklearn.ipynb)

 
Train, register, and deploy an scikit-learn model.

This notebook was developed on the conda pack with slug: *generalml\_p37\_cpu\_v1*

 
`scikit-learn`  `deploy model`  `register model`  `train model`

<sub>Universal Permissive License v 1.0</sup>

---
### - Introduction to SQL Magic
#### [`sql_magic-commands-with-autonomous_database.ipynb`](sql_magic-commands-with-autonomous_database.ipynb)

 
Use SQL Magic commands to work with a database within a Jupytyer notebook. This notebook shows how to to use both line and cell magics.

This notebook was developed on the conda pack with slug: *generalml\_p37\_cpu\_v1*

 
`sql magic`  `autonomous database`

<sub>Universal Permissive License v 1.0</sup>

---
### - Introduction to Streaming
#### [`streaming-service-introduction.ipynb`](streaming-service-introduction.ipynb)

 
Connect to Oracle Cloud Insfrastructure (OCI) Streaming service with kafka.

This notebook was developed on the conda pack with slug: *dataexpl\_p37\_cpu\_v3*

 
`streaming`  `kafka`

<sub>Universal Permissive License v 1.0</sup>

---
### - Train, Register, and Deploy a TensorFlow Model
#### [`train-register-deploy-tensorflow.ipynb`](train-register-deploy-tensorflow.ipynb)

 
Train, register, and deploy a TensorFlow model.

This notebook was developed on the conda pack with slug: *tensorflow27\_p37\_cpu\_v1*

 
`tensorflow`  `deploy model`  `register model`  `train model`

<sub>Universal Permissive License v 1.0</sup>

---
### - Text Extraction Using the Accelerated Data Science (ADS) SDK
#### [`document-text_extraction.ipynb`](document-text_extraction.ipynb)

 
Extract text from common formats (e.g. PDF and Word) into plain text. Customize this process for individual use cases.

This notebook was developed on the conda pack with slug: *nlp\_p37\_cpu\_v2*

 
`text extraction`  `nlp`

<sub>Universal Permissive License v 1.0</sup>

---
### - Train, Register, and Deploy an XGBoost Model
#### [`train-register-deploy-xgboost.ipynb`](train-register-deploy-xgboost.ipynb)

 
Train, register, and deploy an XGBoost model.

This notebook was developed on the conda pack with slug: *generalml\_p37\_cpu\_v1*

 
`xgboost`  `deploy model`  `register model`  `train model`

<sub>Universal Permissive License v 1.0</sup>

---
### - XGBoost with RAPIDS
#### [`xgboost-with-rapids.ipynb`](xgboost-with-rapids.ipynb)

 
Compare training time between CPU and GPU trained models using XGBoost.

This notebook was developed on the conda pack with slug: *rapids2110\_p37\_gpu\_v1*

 
`xgboost`  `rapids`  `gpu`  `machine learning`  `classification`

<sub>Universal Permissive License v 1.0</sup>

---
