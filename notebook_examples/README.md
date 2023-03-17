
ADS Expertise Notebooks
=======================

The [Accelerated Data Science (ADS) SDK](https://accelerated-data-science.readthedocs.io/en/latest/) is maintained by the Oracle Cloud Infrastructure Data Science service team. It speeds up common data science activities by providing tools that automate and/or simplify common data science tasks, along with providing a data scientist friendly pythonic interface to Oracle Cloud Infrastructure (OCI) services, most notably OCI Data Science, Data Flow, Object Storage, and the Autonomous Database. ADS gives you an interface to manage the lifecycle of machine learning models, from data acquisition to model evaluation, interpretation, and model deployment.

The ADS SDK can be downloaded from [PyPi](https://pypi.org/project/oracle-ads/), contributions welcome on [GitHub](https://github.com/oracle/accelerated-data-science)

[![PyPI](https://img.shields.io/pypi/v/oracle-ads.svg)](https://pypi.org/project/oracle-ads/) [![Python](https://img.shields.io/pypi/pyversions/oracle-ads.svg?style=plastic)](https://pypi.org/project/oracle-ads/)

    


## Topics
<img src="https://img.shields.io/badge/deploy model-7-brightgreen"> <img src="https://img.shields.io/badge/register model-7-brightgreen"> <img src="https://img.shields.io/badge/train model-7-brightgreen"> <img src="https://img.shields.io/badge/data flow-4-brightgreen"> <img src="https://img.shields.io/badge/pyspark-4-brightgreen"> <img src="https://img.shields.io/badge/automlx-4-brightgreen"> <img src="https://img.shields.io/badge/oracle open data-3-brightgreen"> <img src="https://img.shields.io/badge/bds-3-brightgreen"> <img src="https://img.shields.io/badge/scikit learn-2-brightgreen"> <img src="https://img.shields.io/badge/big data service-2-brightgreen"> <img src="https://img.shields.io/badge/text classification-2-brightgreen"> <img src="https://img.shields.io/badge/nlp-2-brightgreen"> <img src="https://img.shields.io/badge/regression-2-brightgreen"> <img src="https://img.shields.io/badge/language services-2-brightgreen"> <img src="https://img.shields.io/badge/string manipulation-2-brightgreen"> <img src="https://img.shields.io/badge/regex-2-brightgreen"> <img src="https://img.shields.io/badge/regular expression-2-brightgreen"> <img src="https://img.shields.io/badge/natural language processing-2-brightgreen"> <img src="https://img.shields.io/badge/NLP-2-brightgreen"> <img src="https://img.shields.io/badge/part of speech tagging-2-brightgreen"> <img src="https://img.shields.io/badge/named entity recognition-2-brightgreen"> <img src="https://img.shields.io/badge/sentiment analysis-2-brightgreen"> <img src="https://img.shields.io/badge/custom plugins-2-brightgreen"> <img src="https://img.shields.io/badge/data catalog metastore-2-brightgreen"> <img src="https://img.shields.io/badge/xgboost-2-brightgreen"> <img src="https://img.shields.io/badge/classification-2-brightgreen"> <img src="https://img.shields.io/badge/autonomous database-2-brightgreen"> <img src="https://img.shields.io/badge/intel-1-brightgreen"> <img src="https://img.shields.io/badge/intel extension-1-brightgreen"> <img src="https://img.shields.io/badge/scikit learn-1-brightgreen"> 

## Contents
 - [Audi Autonomous Driving Dataset Repository](#audi-autonomous_driving-oracle_open_data.ipynb)
 - [Building a Forecaster using AutoMLx](#automlx-forecasting.ipynb)
 - [Building and Explaining a Classifier using AutoMLx](#automlx-classifier.ipynb)
 - [Building and Explaining a Regressor using AutoMLx](#automlx-regression.ipynb)
 - [Building and Explaining a Text Classifier using AutoMLx](#automlx-text_classification.ipynb)
 - [Building and Explaining an Anomaly Detector using AutoMLx - Experimental](#automlx-anomaly_detection.ipynb)
 - [Caltech Pedestrian Detection Benchmark Repository](#caltech-pedestrian_detection-oracle_open_data.ipynb)
 - [Connect to Oracle Big Data Service](#big_data_service-(BDS)-kerberos.ipynb)
 - [Graph Analytics and Graph Machine Learning with PyPGX](#pypgx-graph_analytics-machine_learning.ipynb)
 - [How to Read Data with fsspec from Oracle Big Data Service (BDS)](#read-write-big_data_service-(BDS).ipynb)
 - [Intel Extension for Scikit-Learn](#accelerate-scikit_learn-with-intel_extension.ipynb)
 - [Introduction to ADSTuner](#hyperparameter_tuning.ipynb)
 - [Introduction to Model Version Set](#model_version_set.ipynb)
 - [Introduction to SQL Magic](#sql_magic-commands-with-autonomous_database.ipynb)
 - [Introduction to Streaming](#streaming-service-introduction.ipynb)
 - [Introduction to the Oracle Cloud Infrastructure Data Flow Studio](#pyspark-data_flow_studio-introduction.ipynb)
 - [Loading Data With Pandas & Dask](#load_data-object_storage-hive-autonomous-database.ipynb)
 - [Model Evaluation with ADSEvaluator](#model_evaluation-with-ADSEvaluator.ipynb)
 - [Natural Language Processing](#natural_language_processing.ipynb)
 - [PySpark](#pyspark-data_flow-application.ipynb)
 - [Spark NLP within Oracle Cloud Infrastructure Data Flow Studio](#pyspark-data_flow_studio-spark_nlp.ipynb)
 - [Text Classification and Model Explanations using LIME](#text_classification-model_explanation-lime.ipynb)
 - [Text Classification with Data Labeling Service Integration](#data_labeling-text_classification.ipynb)
 - [Text Extraction Using the Accelerated Data Science (ADS) SDK](#document-text_extraction.ipynb)
 - [Train, Register, and Deploy a Generic Model](#train-register-deploy-other-frameworks.ipynb)
 - [Train, Register, and Deploy a LightGBM Model](#train-register-deploy-lightgbm.ipynb)
 - [Train, Register, and Deploy a PyTorch Model](#train-register-deploy-pytorch.ipynb)
 - [Train, Register, and Deploy a TensorFlow Model](#train-register-deploy-tensorflow.ipynb)
 - [Train, Register, and Deploy an XGBoost Model](#train-register-deploy-xgboost.ipynb)
 - [Train, register, and deploy HuggingFace Pipeline](#train-register-deploy-huggingface-pipeline.ipynb)
 - [Train, register, and deploy Sklearn Model](#train-register-deploy-sklearn.ipynb)
 - [Using Data Catalog Metastore with DataFlow](#pyspark-data_catalog-hive_metastore-data_flow.ipynb)
 - [Using Data Catalog Metastore with PySpark](#pyspark-data_catalog-hive_metastore.ipynb)
 - [Using Livy on the Big Data Service](#big_data_service-(BDS)-livy.ipynb)
 - [Visual Genome Repository](#genome_visualization-oracle_open_data.ipynb)
 - [Visualizing Data](#visualizing_data-exploring_data.ipynb)
 - [Working with Pipelines](#pipelines-ml_lifecycle.ipynb)
 - [XGBoost with RAPIDS](#xgboost-with-rapids.ipynb)


## Notebooks
### <a name="automlx-anomaly_detection.ipynb"></a> - Building and Explaining an Anomaly Detector using AutoMLx - Experimental

<sub>Updated: 03/17/2023</sub>
#### [`automlx-anomaly_detection.ipynb`](automlx-anomaly_detection.ipynb)

 
Build an anomaly detection model using the experimental, fully unsupervised anomaly detection pipeline in Oracle AutoMLx for the public Credit Card Fraud dataset.

This notebook was developed on the conda pack with slug: `automlx_p38_cpu_v2`

 
`automlx`  `anomaly detection`

<sub>Universal Permissive License v 1.0</sup>

---
### <a name="automlx-classifier.ipynb"></a> - Building and Explaining a Classifier using AutoMLx

<sub>Updated: 03/17/2023</sub>
#### [`automlx-classifier.ipynb`](automlx-classifier.ipynb)

 
Build a classifier using the Oracle AutoMLx tool and binary data set of Census income data.

This notebook was developed on the conda pack with slug: `automlx_p38_cpu_v2`

 
`automlx`  `classification`  `classifier`

<sub>Universal Permissive License v 1.0</sup>

---
### <a name="automlx-regression.ipynb"></a> - Building and Explaining a Regressor using AutoMLx

<sub>Updated: 03/17/2023</sub>
#### [`automlx-regression.ipynb`](automlx-regression.ipynb)

 
Build a regressor using Oracle AutoMLx and a pricing data set. Training options will be explored and the resulting AutoMLx models will be evaluated.

This notebook was developed on the conda pack with slug: `automlx_p38_cpu_v2`

 
`automlx`  `regression`

<sub>Universal Permissive License v 1.0</sup>

---
### <a name="automlx-text_classification.ipynb"></a> - Building and Explaining a Text Classifier using AutoMLx

<sub>Updated: 03/17/2023</sub>
#### [`automlx-text_classification.ipynb`](automlx-text_classification.ipynb)

 
build a classifier using the Oracle AutoMLx tool for the public 20newsgroup dataset

This notebook was developed on the conda pack with slug: `automlx_p38_cpu_v2`

 
`automlx`  `text classification`  `text classifier`

<sub>Universal Permissive License v 1.0.</sup>

---
### <a name="audi-autonomous_driving-oracle_open_data.ipynb"></a> - Audi Autonomous Driving Dataset Repository

<sub>Updated: 12/22/2022</sub>
#### [`audi-autonomous_driving-oracle_open_data.ipynb`](audi-autonomous_driving-oracle_open_data.ipynb)

 
Download, process and display autonomous driving data, and map LiDAR data onto images.

This notebook was developed on the conda pack with slug: `computervision_p37_cpu_v1`

 
`autonomous driving`  `oracle open data`

<sub>Universal Permissive License v 1.0</sup>

---
### <a name="big_data_service-(BDS)-livy.ipynb"></a> - Using Livy on the Big Data Service

<sub>Updated: 12/22/2022</sub>
#### [`big_data_service-(BDS)-livy.ipynb`](big_data_service-(BDS)-livy.ipynb)

 
Work interactively with a BDS cluster using Livy and two different connection techniques, SparkMagic (for a notebook environment) and with REST.

This notebook was developed on the conda pack with slug: `pyspark30_p37_cpu_v5`

 
`bds`  `big data service`  `livy`

<sub>Universal Permissive License v 1.0</sup>

---
### <a name="read-write-big_data_service-(BDS).ipynb"></a> - How to Read Data with fsspec from Oracle Big Data Service (BDS)

<sub>Updated: 12/22/2022</sub>
#### [`read-write-big_data_service-(BDS).ipynb`](read-write-big_data_service-(BDS).ipynb)

 
Manage data using fsspec file system. Read and save data using pandas and pyarrow through fsspec file system.

This notebook was developed on the conda pack with slug: `pyspark30_p37_cpu_v5`

 
`bds`  `fsspec`

<sub>Universal Permissive License v 1.0</sup>

---
### <a name="caltech-pedestrian_detection-oracle_open_data.ipynb"></a> - Caltech Pedestrian Detection Benchmark Repository

<sub>Updated: 12/22/2022</sub>
#### [`caltech-pedestrian_detection-oracle_open_data.ipynb`](caltech-pedestrian_detection-oracle_open_data.ipynb)

 
Download and process annotated video data of vehicles and pedestrians.

This notebook was developed on the conda pack with slug: `generalml_p38_cpu_v1`

 
`caltech`  `pedestrian detection`  `oracle open data`

<sub>Universal Permissive License v 1.0</sup>

---
### <a name="pyspark-data_catalog-hive_metastore-data_flow.ipynb"></a> - Using Data Catalog Metastore with DataFlow

<sub>Updated: 12/22/2022</sub>
#### [`pyspark-data_catalog-hive_metastore-data_flow.ipynb`](pyspark-data_catalog-hive_metastore-data_flow.ipynb)

 
Write and test a Data Flow batch application using the Oracle Cloud Infrastructure (OCI) Data Catalog Metastore. Configure the job, run the application and clean up resources.

This notebook was developed on the conda pack with slug: `pyspark30_p37_cpu_v5`

 
`data catalog metastore`  `data flow`

<sub>Universal Permissive License v 1.0</sup>

---
### <a name="data_labeling-text_classification.ipynb"></a> - Text Classification with Data Labeling Service Integration

<sub>Updated: 12/22/2022</sub>
#### [`data_labeling-text_classification.ipynb`](data_labeling-text_classification.ipynb)

 
Use the Oracle Cloud Infrastructure (OCI) Data Labeling service to efficiently build enriched, labeled datasets for the purpose of accurately training AI/ML models. This notebook demonstrates operations that can be performed using the Advanced Data Science (ADS) Data Labeling module.

This notebook was developed on the conda pack with slug: `nlp_p37_cpu_v2`

 
`data labeling`  `text classification`

<sub>Universal Permissive License v 1.0</sup>

---
### <a name="visualizing_data-exploring_data.ipynb"></a> - Visualizing Data

<sub>Updated: 12/22/2022</sub>
#### [`visualizing_data-exploring_data.ipynb`](visualizing_data-exploring_data.ipynb)

 
Perform common data visualization tasks and explore data with the ADS SDK. Plotting approaches include 3D plots, pie chart, GIS plots, and Seaborn pairplot graphs.

This notebook was developed on the conda pack with slug: `generalml_p38_cpu_v1`

 
`data visualization`  `seaborn plot`  `charts`

<sub>Universal Permissive License v 1.0</sup>

---
### <a name="pyspark-data_catalog-hive_metastore.ipynb"></a> - Using Data Catalog Metastore with PySpark

<sub>Updated: 12/22/2022</sub>
#### [`pyspark-data_catalog-hive_metastore.ipynb`](pyspark-data_catalog-hive_metastore.ipynb)

 
Configure and use PySpark to process data in the Oracle Cloud Infrastructure (OCI) Data Catalog metastore, including common operations like creating and loading data from the metastore.

This notebook was developed on the conda pack with slug: `pyspark30_p37_cpu_v5`

 
`dcat`  `data catalog metastore`  `pyspark`

<sub>Universal Permissive License v 1.0</sup>

---
### <a name="train-register-deploy-other-frameworks.ipynb"></a> - Train, Register, and Deploy a Generic Model

<sub>Updated: 12/22/2022</sub>
#### [`train-register-deploy-other-frameworks.ipynb`](train-register-deploy-other-frameworks.ipynb)

 
Train, register, and deploy a generic model

This notebook was developed on the conda pack with slug: `generalml_p38_cpu_v1`

 
`generic model`  `deploy model`  `register model`  `train model`

<sub>Universal Permissive License v 1.0</sup>

---
### <a name="train-register-deploy-huggingface-pipeline.ipynb"></a> - Train, register, and deploy HuggingFace Pipeline

<sub>Updated: 03/06/2023</sub>
#### [`train-register-deploy-huggingface-pipeline.ipynb`](train-register-deploy-huggingface-pipeline.ipynb)

 
Train, register, and deploy a huggingface pipeline.

This notebook was developed on the conda pack with slug: `pytorch110_p38_cpu_v1`

 
`huggingface`  `deploy model`  `register model`  `train model`

<sub>Universal Permissive License v 1.0</sup>

---
### <a name="hyperparameter_tuning.ipynb"></a> - Introduction to ADSTuner

<sub>Updated: 12/22/2022</sub>
#### [`hyperparameter_tuning.ipynb`](hyperparameter_tuning.ipynb)

 
Use ADSTuner to optimize an estimator using the scikit-learn API

This notebook was developed on the conda pack with slug: `generalml_p38_cpu_v1`

 
`hyperparameter tuning`

<sub>Universal Permissive License v 1.0</sup>

---
### <a name="accelerate-scikit_learn-with-intel_extension.ipynb"></a> - Intel Extension for Scikit-Learn

<sub>Updated: 12/22/2022</sub>
#### [`accelerate-scikit_learn-with-intel_extension.ipynb`](accelerate-scikit_learn-with-intel_extension.ipynb)

 
Enhance performance of scikit-learn models using the Intel(R) oneAPI Data Analytics Library. Train a k-means model using both sklearn and the accelerated Intel library and compare performance.

This notebook was developed on the conda pack with slug: `sklearnex202130_p37_cpu_v1`

 
`intel`  `intel extension`  `scikit-learn`  `scikit learn`

<sub>Universal Permissive License v 1.0</sup>

---
### <a name="big_data_service-(BDS)-kerberos.ipynb"></a> - Connect to Oracle Big Data Service

<sub>Updated: 12/22/2022</sub>
#### [`big_data_service-(BDS)-kerberos.ipynb`](big_data_service-(BDS)-kerberos.ipynb)

 
Connect to Oracle Big Data services using Kerberos.

This notebook was developed on the conda pack with slug: `pyspark30_p37_cpu_v5`

 
`kerberos`  `big data service`  `bds`

<sub>Universal Permissive License v 1.0</sup>

---
### <a name="natural_language_processing.ipynb"></a> - Natural Language Processing

<sub>Updated: 12/22/2022</sub>
#### [`natural_language_processing.ipynb`](natural_language_processing.ipynb)

 
Use the ADS SDK to process and manipulate strings. This notebook includes regular expression matching and natural language (NLP) parsing, including part-of-speech tagging, named entity recognition, and sentiment analysis. It also shows how to create and use custom plugins specific to your specific needs.

This notebook was developed on the conda pack with slug: `nlp_p37_cpu_v2`

 
`language services`  `string manipulation`  `regex`  `regular expression`  `natural language processing`  `NLP`  `part-of-speech tagging`  `named entity recognition`  `sentiment analysis`  `custom plugins`

<sub>Universal Permissive License v 1.0</sup>

---
### <a name="automlx-forecasting.ipynb"></a> - Building a Forecaster using AutoMLx

<sub>Updated: 03/17/2023</sub>
#### [`automlx-forecasting.ipynb`](automlx-forecasting.ipynb)

 
Use Oracle AutoMLx to build a forecast model with real-world data sets.

This notebook was developed on the conda pack with slug: `automlx_p38_cpu_v2`

 
`language services`  `string manipulation`  `regex`  `regular expression`  `natural language processing`  `NLP`  `part-of-speech tagging`  `named entity recognition`  `sentiment analysis`  `custom plugins`

<sub>Universal Permissive License v 1.0</sup>

---
### <a name="train-register-deploy-lightgbm.ipynb"></a> - Train, Register, and Deploy a LightGBM Model

<sub>Updated: 12/22/2022</sub>
#### [`train-register-deploy-lightgbm.ipynb`](train-register-deploy-lightgbm.ipynb)

 
Train, register, and deploy a LightGBM model.

This notebook was developed on the conda pack with slug: `generalml_p38_cpu_v1`

 
`lightgbm`  `deploy model`  `register model`  `train model`

<sub>Universal Permissive License v 1.0</sup>

---
### <a name="load_data-object_storage-hive-autonomous-database.ipynb"></a> - Loading Data With Pandas & Dask

<sub>Updated: 01/09/2023</sub>
#### [`load_data-object_storage-hive-autonomous-database.ipynb`](load_data-object_storage-hive-autonomous-database.ipynb)

 
Load data from sources including ADW, Object Storage, and Hive in formats like parquet, csv etc

This notebook was developed on the conda pack with slug: `generalml_p38_cpu_v1`

 
`loading data`  `autonomous database`  `adw`  `hive`  `pandas`  `dask`  `object storage`

<sub>Universal Permissive License v 1.0</sup>

---
### <a name="model_version_set.ipynb"></a> - Introduction to Model Version Set

<sub>Updated: 02/03/2023</sub>
#### [`model_version_set.ipynb`](model_version_set.ipynb)

 
A model version set is a way to track the relationships between models. As a container, the model version set takes a collection of models. Those models are assigned a sequential version number based on the order they are entered into the model version set.

This notebook was developed on the conda pack with slug: `dbexp_p38_cpu_v1`

 
`model`  `model experiments`  `model version set`

<sub>Universal Permissive License v 1.0</sup>

---
### <a name="model_evaluation-with-ADSEvaluator.ipynb"></a> - Model Evaluation with ADSEvaluator

<sub>Updated: 12/22/2022</sub>
#### [`model_evaluation-with-ADSEvaluator.ipynb`](model_evaluation-with-ADSEvaluator.ipynb)

 
Train and evaluate different types of models: binary classification using an imbalanced dataset, multi-class classification using a synthetically generated dataset consisting of three equally distributed classes, and a regression using a synthetically generated dataset with positive targets.

This notebook was developed on the conda pack with slug: `generalml_p38_cpu_v1`

 
`model evaluation`  `binary classification`  `regression`  `multi-class classification`  `imbalanced dataset`  `synthetic dataset`

<sub>Universal Permissive License v 1.0</sup>

---
### <a name="text_classification-model_explanation-lime.ipynb"></a> - Text Classification and Model Explanations using LIME

<sub>Updated: 12/22/2022</sub>
#### [`text_classification-model_explanation-lime.ipynb`](text_classification-model_explanation-lime.ipynb)

 
Perform model explanations on an NLP classifier using the locally interpretable model explanations technique (LIME).

This notebook was developed on the conda pack with slug: `nlp_p37_cpu_v2`

 
`nlp`  `lime`  `model_explanation`  `text_classification`  `text_explanation`

<sub>Universal Permissive License v 1.0</sup>

---
### <a name="genome_visualization-oracle_open_data.ipynb"></a> - Visual Genome Repository

<sub>Updated: 12/22/2022</sub>
#### [`genome_visualization-oracle_open_data.ipynb`](genome_visualization-oracle_open_data.ipynb)

 
Load visual data, define regions, and visualize objects using metadata to connect structured images to language.

This notebook was developed on the conda pack with slug: `generalml_p38_cpu_v1`

 
`object annotation`  `genome visualization`  `oracle open data`

<sub>Universal Permissive License v 1.0 (https://oss.oracle.com/licenses/upl/)</sup>

---
### <a name="pipelines-ml_lifecycle.ipynb"></a> - Working with Pipelines

<sub>Updated: 02/03/2023</sub>
#### [`pipelines-ml_lifecycle.ipynb`](pipelines-ml_lifecycle.ipynb)

 
Create and use ML pipelines through the entire machine learning lifecycle

This notebook was developed on the conda pack with slug: `generalml_p38_cpu_v1`

 
`pipelines`  `pipeline step`  `jobs pipeline`

<sub>Universal Permissive License v 1.0</sup>

---
### <a name="pypgx-graph_analytics-machine_learning.ipynb"></a> - Graph Analytics and Graph Machine Learning with PyPGX

<sub>Updated: 03/13/2023</sub>
#### [`pypgx-graph_analytics-machine_learning.ipynb`](pypgx-graph_analytics-machine_learning.ipynb)

 
Use Oracle's Graph Analytics libraries to demonstrate graph algorithms, graph machine learning models, and use the property graph query language (PGQL)

This notebook was developed on the conda pack with slug: `pypgx2310_p38_cpu_v1`

 
`pypgx`  `graph analytics`  `pgx`

<sub>Universal Permissive License v 1.0</sup>

---
### <a name="pyspark-data_flow-application.ipynb"></a> - PySpark

<sub>Updated: 12/22/2022</sub>
#### [`pyspark-data_flow-application.ipynb`](pyspark-data_flow-application.ipynb)

 
Develop local PySpark applications and work with remote clusters using Data Flow.

This notebook was developed on the conda pack with slug: `pyspark24_p37_cpu_v3`

 
`pyspark`  `data flow`

<sub>Universal Permissive License v 1.0</sup>

---
### <a name="pyspark-data_flow_studio-introduction.ipynb"></a> - Introduction to the Oracle Cloud Infrastructure Data Flow Studio

<sub>Updated: 12/22/2022</sub>
#### [`pyspark-data_flow_studio-introduction.ipynb`](pyspark-data_flow_studio-introduction.ipynb)

 
Run interactive Spark workloads on a long lasting Oracle Cloud Infrastructure Data Flow Spark cluster through Apache Livy integration. Data Flow Spark Magic is used for interactively working with remote Spark clusters through Livy, a Spark REST server, in Jupyter notebooks. It includes a set of magic commands for interactively running Spark code.

This notebook was developed on the conda pack with slug: `pyspark32_p38_cpu_v2`

 
`pyspark`  `data flow`

<sub>Universal Permissive License v 1.0</sup>

---
### <a name="pyspark-data_flow_studio-spark_nlp.ipynb"></a> - Spark NLP within Oracle Cloud Infrastructure Data Flow Studio

<sub>Updated: 12/22/2022</sub>
#### [`pyspark-data_flow_studio-spark_nlp.ipynb`](pyspark-data_flow_studio-spark_nlp.ipynb)

 
Demonstrates how to use Spark NLP within a long lasting Oracle Cloud Infrastructure Data Flow cluster.

This notebook was developed on the conda pack with slug: `pyspark32_p38_cpu_v1`

 
`pyspark`  `data flow`

<sub>Universal Permissive License v 1.0</sup>

---
### <a name="train-register-deploy-pytorch.ipynb"></a> - Train, Register, and Deploy a PyTorch Model

<sub>Updated: 02/10/2023</sub>
#### [`train-register-deploy-pytorch.ipynb`](train-register-deploy-pytorch.ipynb)

 
Train, register, and deploy a PyTorch model.

This notebook was developed on the conda pack with slug: `pytorch110_p38_cpu_v1`

 
`pytorch`  `deploy model`  `register model`  `train model`

<sub>Universal Permissive License v 1.0</sup>

---
### <a name="train-register-deploy-sklearn.ipynb"></a> - Train, register, and deploy Sklearn Model

<sub>Updated: 12/22/2022</sub>
#### [`train-register-deploy-sklearn.ipynb`](train-register-deploy-sklearn.ipynb)

 
Train, register, and deploy an scikit-learn model.

This notebook was developed on the conda pack with slug: `generalml_p38_cpu_v1`

 
`scikit-learn`  `deploy model`  `register model`  `train model`

<sub>Universal Permissive License v 1.0</sup>

---
### <a name="sql_magic-commands-with-autonomous_database.ipynb"></a> - Introduction to SQL Magic

<sub>Updated: 02/02/2023</sub>
#### [`sql_magic-commands-with-autonomous_database.ipynb`](sql_magic-commands-with-autonomous_database.ipynb)

 
Use SQL Magic commands to work with a database within a Jupyter notebook. This notebook shows how to to use both line and cell magics.

This notebook was developed on the conda pack with slug: `generalml_p38_cpu_v1`

 
`sql magic`  `autonomous database`

<sub>Universal Permissive License v 1.0</sup>

---
### <a name="streaming-service-introduction.ipynb"></a> - Introduction to Streaming

<sub>Updated: 01/02/2023</sub>
#### [`streaming-service-introduction.ipynb`](streaming-service-introduction.ipynb)

 
Connect to Oracle Cloud Insfrastructure (OCI) Streaming service with kafka.

This notebook was developed on the conda pack with slug: `dataexpl_p37_cpu_v3`

 
`streaming`  `kafka`

<sub>Universal Permissive License v 1.0</sup>

---
### <a name="train-register-deploy-tensorflow.ipynb"></a> - Train, Register, and Deploy a TensorFlow Model

<sub>Updated: 12/22/2022</sub>
#### [`train-register-deploy-tensorflow.ipynb`](train-register-deploy-tensorflow.ipynb)

 
Train, register, and deploy a TensorFlow model.

This notebook was developed on the conda pack with slug: `tensorflow28_p38_cpu_v1`

 
`tensorflow`  `deploy model`  `register model`  `train model`

<sub>Universal Permissive License v 1.0</sup>

---
### <a name="document-text_extraction.ipynb"></a> - Text Extraction Using the Accelerated Data Science (ADS) SDK

<sub>Updated: 12/22/2022</sub>
#### [`document-text_extraction.ipynb`](document-text_extraction.ipynb)

 
Extract text from common formats (e.g. PDF and Word) into plain text. Customize this process for individual use cases.

This notebook was developed on the conda pack with slug: `nlp_p37_cpu_v2`

 
`text extraction`  `nlp`

<sub>Universal Permissive License v 1.0</sup>

---
### <a name="train-register-deploy-xgboost.ipynb"></a> - Train, Register, and Deploy an XGBoost Model

<sub>Updated: 12/22/2022</sub>
#### [`train-register-deploy-xgboost.ipynb`](train-register-deploy-xgboost.ipynb)

 
Train, register, and deploy an XGBoost model.

This notebook was developed on the conda pack with slug: `generalml_p38_cpu_v1`

 
`xgboost`  `deploy model`  `register model`  `train model`

<sub>Universal Permissive License v 1.0</sup>

---
### <a name="xgboost-with-rapids.ipynb"></a> - XGBoost with RAPIDS

<sub>Updated: 12/22/2022</sub>
#### [`xgboost-with-rapids.ipynb`](xgboost-with-rapids.ipynb)

 
Compare training time between CPU and GPU trained models using XGBoost

This notebook was developed on the conda pack with slug: `rapids2110_p37_gpu_v1`

 
`xgboost`  `rapids`  `gpu`  `machine learning`  `classification`

<sub>Universal Permissive License v 1.0</sup>

---
