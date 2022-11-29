# DF: Move a column to a given position

## Use case

You can use it to move the specified column to a specific position in the input csv.

## Prerequisites
Follow the [guide](README.md) and setup your policies correctly.

Also, for csv, you can use [utility-meter-readings](../sample_datasets/utility-meter-readings.csv) as an example.

## Steps

Download the example Spark application: [move_column.py](./example_code/move_column.py)

Upload the code to OCI Object Storage(in case of Scala or Java, upload the compiled JAR file). 

Also, upload the csv file waiting to be processed to the OCI Object Storage. It can be either the same Object Storage as the code or a different one. 

## Start DataFlow


Go to **Analytics & AI** > **Data Flow** > click **Create application**.

Select the language and code file accordingly. Here we are using Python.

![image info](./utils/select-move_column-code.png)


Add the following to the arguments:

```
--input ${input} --column_name ${column_name} --position ${position} --output ${output}
```

(unlikely) or, if you want to [coalesce](https://spark.apache.org/docs/latest/api/python/reference/api/pyspark.RDD.coalesce.html) your data frame, all a `--coalesce` flag to your argument list:
```
--input ${input} --column_name ${column_name} --position ${position} --output ${output} --coalesce
```

- <b>input</b> points to the input data source. Notice you will need to specify the full oci file path by following the format `oci://<bucket-name>@<namespace>/<path-to-file>`. `bucket-name` and `namespace` can be found at your bucket details under **Object Storage**.
- <b>output</b> is similar to <b>input</b>, except the `<path-to-file>` should be change to a `<folder-path>`, since the output file will be written to your specified folder.
- <b>columns_name</b> is a column you want to move to the position specified. In my example, I have a csv with column name `col1` , which I want to move to position `2`.
-<b>position</b> is the position of the column where the specified column needs to be moved. In my example, I have a csv with column name `col1` , which I want to move to position `2`
![image info](./utils/move_column-code-parameters.png)

Finally, choose the bucket to save the application log. In case there is failure during execution, you can check what's going on there.

Click "Save changes" to save the Application.


## Execution and result
Click **Run** on your application. Once the execution succeeds, go to your specified bucket and check result.
Note : position argument should be between 0 and number of columns

[Data preprocessing workflow](../README.md)

## Troubleshooting

If the run fails 
1. Output file already exists.; - update the output argument with new file name 
2. ValueError 'position value should be between 0 and number of columns in the input data' - check the position argument value range.  
