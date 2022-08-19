## Anomaly Detection

[Oracle Cloud Infrastructure (OCI) Anomaly Detection](https://www.oracle.com/artificial-intelligence/anomaly-detection/)
is a multi-tenanted AI service that 
enables developers to easily build business-specific anomaly detection models that flag 
critical incidents, resulting in faster time to detection and resolution. Specialized APIs 
and automated model selection simplify training and deploying anomaly detection 
models to applications and operations—all without data science experience. Oracle’s AD 
algorithms are backed by more than 150 patents, and capable of detecting anomalies 
earlier with fewer false alarms. These algorithms work together to ensure higher 
sensitivity and better false alarm avoidance than other traditional machine learning 
approaches, such as neural nets and support vector machines. It provides 
comprehensive set of APIs to help developers upload raw data, train the anomaly 
detection model using their own business-specific data, and detect anomalies from the 
stored model. AD service takes care of underline infrastructure and scaling 
requirements, freeing up developers to focus on creating applications and solutions to 
achieve their business objectives. 
Note: You can quickly explore OCI Anomaly Detection Service in OCI LiveLabs 
[Get Started with OCI Anomaly Detection Workshop](https://apexapps.oracle.com/pls/apex/dbpm/r/livelabs/view-workshop?wid=819&clear=180&session=1329701598349)

Although it is very easy to configure and use AD service, users must ensure that input data 
meets AD’s [Input Data requirements](https://docs.oracle.com/en-us/iaas/Content/anomaly/using/data-require.htm#data_require).
In many instances, users are advised to use [OCI 
Data Integration](https://docs.oracle.com/en-us/iaas/data-integration/home.htm) (DIS) or [OCI Data Flow](https://www.oracle.com/big-data/data-flow/) (DF) to transform, pre-process and convert data 
into to meet AD’s [input specifications](https://docs.oracle.com/en-us/iaas/Content/anomaly/using/data-require.htm#data_require), which can be a bit of learning curve for AD users. 
This is where this Git Repo can be very helpful. This repo provides multiple examples of 
common AD pre-processing steps using DIS and DF, that can be used by users as 
templates to build end-to-end solution.

[DF:  Common Pre-Processing Workflow used in Anomaly Detection](data_preprocessing_examples/oci_data_flow_based_examples)

[DIS: Common Pre-Processing Workflow used in Anomaly Detection](data_preprocessing_examples/oci_data_integration_based_examples)

### When should I use DF vs DIS?

While both DF and DIS are sophisticated platforms that can be used to address your pre-processing needs,
you may find DF performing faster for large datasets(more than 100k rows or so) when a sufficient number of parallel Executors are configured.
Also, DF is able to handle more columns, and certain specialized data preprocessing tasks such as batching, sharding and pivoting on multiple columns.
DIS provides an easy-to-understand drag and drop interface which does not require any programming expertise, and provides ability to preview and validate transformations.
If you do not have any of the specialized data preprocessing needs mentioned above, DIS is a good option.
