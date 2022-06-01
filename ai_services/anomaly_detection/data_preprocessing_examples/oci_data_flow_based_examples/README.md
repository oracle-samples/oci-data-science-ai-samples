# DF: Common Preprocessing Workflow

## Data Flow Policy Setup

### User Policies
1.	Create a group in your identity service called `dataflow-users` and add users to this group.
2.	Create two buckets in your compartment, e.g. `dataflow-logs` and `dataflow-warehouse`.
3.	Create a policy and add the following statements:

```
Allow group dataflow-users to manage objects in compartment compartment_name where ALL {target.bucket.name='dataflow-logs', any {request.permission='OBJECT_CREATE', request.permission='OBJECT_INSPECT'}}
```

```
Allow group dataflow-users to manage dataflow-family in compartment compartment_name where any {request.user.id = target.user.id, request.permission = 'DATAFLOW_APPLICATION_CREATE', request.permission = 'DATAFLOW_RUN_CREATE'}
```

```
Allow group dataflow-users to read buckets in compartment compartment_name
Allow group dataflow-users to use dataflow-family in compartment compartment_name
```
### Service Policies
The Data Flow service needs permission to perform actions on behalf of the user or group on objects within the tenancy. Create a policy called *dataflow-service* and add the following statement:
```
Allow service dataflow to read objects in compartment compartment_name where target.bucket.name='dataflow-logs'
Allow service dataflow to read objects in compartment compartment_name where target.bucket.name='dataflow-warehouse'
```


## Create an OCI Data Flow Application for Preprocessing

Download the PySpark code sample for the preprocessing task you need, and upload it to object storage.


1. [DF: Feature Normalization](feature_normalization.md)
2. [DF: Fixed Window Batching](Fixed_window_batching.md)
3. [DF: Multiple Input Sources](multiple_input_sources.md)
4. [DF: Pivoting](pivoting.md)
5. [DF: Sharding](sharding.md)
6. [DF: Sliding Window Aggregation](sliding_window_aggregation.md)
7. [DF: Time Series Join](time_series_join.md)
8. [DF: Time series merge](time_series_merge.md)
9. [DF: Date-time conversion](date_time_conversion.md)
10.[DF: Remove Unnecessary Columns](remove_unnecessary_columns.md)
11.[DF: String Replacement](string_replacement.md)
12.[DF: Temporal Differencing](temporal_differencing.md)
13.[DF: One-hot encoding](one_hot_encoding.md)


Upload your data files to Object Storage using the same process, and keep track of the path to the data.

## Run the Preprocessing Task

```
1. In the sandwich menu, choose Analytics and AI > Data Flow.


2. Select your Application.


3. Click "Run". Assign values to each of the parameters as mentioned in the application


4. Track the status of the run in "Runs". After it finishes successfully, the output file is written to target location.
```
