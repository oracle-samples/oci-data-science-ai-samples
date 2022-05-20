# DF: Downsampling

## Use case

The user wants to downsample the data based on a user-defined downsampling rate to attain larger time footprint on the data.
## Steps


Download the example Spark application: [downsampling.py](./example_code/downsampling.py)

Upload the code to OCI Object Storage(in case of Scala or Java, upload the compiled JAR file). Note the path to the code eg. bucket dataflow-
warehouse, root folder, file name downsampling.py.

If there are multiple files, ensure they are all in the same folder

![image info](./utils/upload_object.png)
## Create an Application

```
Click "Create Application"
```

![image info](./utils/DW1.png)

```
Select the number of Executors, logging location and path to the Spark application that we just created. If you are entering the path manually, it needs to
be specified in the following format: oci://dataflow-warehouse@<compartmentID>/pivoting.py where <compartmentID> is the compartment name. Otherwise,
you can use the browser to choose an object
```

Add the following to the arguments:

```
--input ${input} --window_size ${window_size} --output ${output} --coalesce ${coalesce}
```
<b>input</b> points to the input data source. <window_size> refers to the user-defined downsampling rate. This should be an integer.


```
Specify path in Object Storage to store logs. These may be useful later for troubleshooting.
```
![image info](./utils/P6.png)


```
Click "Save changes" to save the Application
```


