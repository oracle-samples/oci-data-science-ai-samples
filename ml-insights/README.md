# Oracle Machine Learning Observability Insights Library (ML Insights)
ML Insights is a python library for data scientists, ML engineers and developers. Insights can be used to ingest data in different formats, apply row based transformations and monitor data and ML Models from validation to production.

ML Insights library also provides many ways to process and evaluate data and ML models. The options include low code alternative for customisation, a pre-built application and and further extensibility through custom applications and custom components.

## Installation
ML Insights can be installed in a python 3.8 environment using:
```bash
pip install oracle-ml-insights
```
Several ML Insights dependencies are optional (for eg: Execution Engine) and can be installed with:
```bash
pip install oracle-ml-insights[option]
```
where "option" can be one of:

- "dask", to run ML Insights on Dask Execution Engine

## How it works
ML Insights helps evaluate and monitor data and ML model for entirety of ML Observability lifecycle.

Insights is component based where each component has a specific responsibility with a workflow managing the individual components.

Insights provides components to carry out tasks like data ingestion, row level data transformation, metric calculation and post processing of metric output. More details on these are covered in the Getting Started section.

In very simple terms, one has to provide location to the input data set that needs to be processed, select any additional simple transformation needed on the input data (for example, converting an un-structured column to structured one), and decide which metrics should be calculated for different features (columns of data). The user can also decide to define some post-action to be performed once all the metrics have been calculated.

Insights provides a simple, declarative API, out of box components covering majority of common use cases to choose from. Also, Insights enables users to author json-based configurations that can be used to define and customise all of its core features.

 - Insights currently supports CSV, JSON, and JSONL data types.

 - It also supports major execution engines like Native Pandas, Dask, and Spark.

 - Insights provides metrics in different groups like
    - Data Integrity
    - Data Quality/ Summary
    - Feature and Prediction Drift Detection
    - Model Performance for both classification and Regression Models

 - Insights also supports integration for writing metric data, or connecting to OCI monitoring service.

## Examples

| Jupyter Notebook                                                                                                                       | 
|----------------------------------------------------------------------------------------------------------------------------------------|
| [Minimal ML Insight to calculate metrics](./sample_notebooks/1_Minimal_ML_Insights.ipynb)                                              | 
| [Run ML Insight Using Config File](./sample_notebooks/2_Run_ML_Insights_using_config_file.ipynb)                                       |
| [Run ML Insight using APIs](./sample_notebooks/3_Run_ML_Insights_using_api.ipynb)                                                      |
| [ML Insights Data Reader & Data Source Example](./sample_notebooks/4_Data_Source_and_Reader_Example.ipynb)                             |
| [ML Insights : Post Processor Component Example.](./sample_notebooks/5_Post_Processor_Profile_Writer_Example.ipynb)                    |
| [ML Insights : Data Quality & Data Integrity Metrics](./sample_notebooks/6_Data_Quality_and_Data_Integrity_Metrics.ipynb)              |
| [ML Insights : Performance Metrics For Classification Models](./sample_notebooks/7_Performance_Metric_For_Classification_Models.ipynb) |
| [ML Insights Conflict Metrics](./sample_notebooks/8_Conflict_Metrics.ipynb)                                                            |
| [ML Insights : Performance Metrics For Regression Models](./sample_notebooks/9_Performance_Metrics_for_Regression_Model.ipynb)         |
| [ML Insights : Drift Metrics](./sample_notebooks/10_Drift_Metrics.ipynb)                                                               |
| [ML Insights : Data Correlation Metrics](./sample_notebooks/11_Data_Correlation_Metrics.ipynb)                                         |
| [ML Insights run with Custom Metrics](./sample_notebooks/12_Custom_Metrics_Example.ipynb)                                              |

## Note
The files [sum_divide_by_k_custom_metrics.py](./sample_notebooks/sum_divide_by_k_custom_metrics.py) and [sum_divide_by_two_custom_metrics.py](./sample_notebooks/sum_divide_by_two_custom_metrics.py) are examples of how to implement custom metrics and usage is demonstrated in sample notebook [ML Insights run with Custom Metrics](./sample_notebooks/12_Custom_Metrics_Example.ipynb).  


