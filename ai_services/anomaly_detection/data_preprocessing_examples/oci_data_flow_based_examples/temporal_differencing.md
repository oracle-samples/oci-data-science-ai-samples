# DF: Temporal Differencing

## Use case

The user wants to temporally differentiate the data on a desired predefined rate.

## Steps

Download the example Spark application: [temporal_differencing.py](./example_code/temporal_differencing.py)

Upload the code to OCI Object Storage(in case of Scala or Java, upload the compiled JAR file). Note the path to the code eg. bucket dataflow-
warehouse, root folder, file name temporal_differencing.py.

If there are multiple files, ensure they are all in the same folder

![image info](./utils/upload_object.png)
## Create an Application

```
Click "Create Application"
```

![image info](./utils/TD1.png)

```
Select the number of Executors, logging location and path to the Spark application that we just created. If you are entering the path manually, it needs to
be specified in the following format: oci://dataflow-warehouse@<compartmentID>/pivoting.py where <compartmentID> is the compartment name. Otherwise,
you can use the browser to choose an object
```

Add the following to the arguments:

```
--input ${input} --diff_factor ${diff_factor} --output ${output} --coalesce ${coalesce}
```
<b>input</b> points to the input data source. <b>diff_factor</b> refers to the temporal difference taken into account. This should be an integer.


```
Specify path in Object Storage to store logs. These may be useful later for troubleshooting.
```
![image info](./utils/P6.png)


```
Click "Save changes" to save the Application
```


