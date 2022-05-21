# DF: Common Preprocessing Workflow

## Set up Data Flow


Refer to this documentation to


Create resources (compartment, network and user group) for DF.
Create policies to use Data Flow.
Create policies for Data Flow to access data sources.
Create policies for Data Flow to access your Spark application code.

## Create an OCI Data Flow Application for Preprocessing

Download the PySpark code sample for the preprocessing task you need, and upload it to object storage.


1. [DF: Feature Normalization](./feature_normalization.md)
2. [DF: Fixed Window Batching](./fixed_window_batching.md)
3. [DF: Multiple Input Sources](./Multiple_input_sources.md)
4. [DF: Pivoting](./pivoting.md)
5. [DF: Sharding](./sharding.md)
6. [DF: Sliding Window Aggregation](./sliding_window_aggregation.md)
7. [DF: Time Series Join](./time_series_join.md)
8. [DF: Time series merge](./time_series_merge.md)
9. [DF: Date-time conversion](./date_time_conversion.md)
10. [DF: Remove Unnecessary Columns](./Remove_unnecessary_columns.md)
11. [DF: String Replacement](string_replacement.md)
12. [DF: Temporal Differencing](./Temporal_differencing.md) 
13. [DF: One-hot encoding](./one_hot_encoding.md)


Upload your data files to Object Storage using the same process, and keep track of the path to the data.

## Run the Preprocessing Task

```
1. In the sandwich menu, choose Analytics and AI > Data Flow.



2. Select your Application.

3. Click "Run". Assign values to each of the parameters as mentioned in the application


4. Track the status of the run in "Runs". After it finishes successfully, the output file is written to target location.
```


