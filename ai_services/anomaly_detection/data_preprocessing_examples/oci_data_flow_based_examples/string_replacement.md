# DF: String transformations

## Use case

The user wants to perform basic string transformations on a particular or set of columns.
## Steps


Download the example Spark application: [string_transformations.py](./example_code/string_transformations.py).

Upload the code to OCI Object Storage(in case of Scala or Java, upload the compiled JAR file). Note the path to the code eg. bucket dataflow-
warehouse, root folder, file name string_transformations.py.

If there are multiple files, ensure they are all in the same folder

![image info](./utils/upload_object.png)
## Create an Application

```
Click "Create Application"
```

![image info](./utils/ST1.png)

```
Select the number of Executors, logging location and path to the Spark application that we just created. If you are entering the path manually, it needs to
be specified in the following format: oci://dataflow-warehouse@<compartmentID>/pivoting.py where <compartmentID> is the compartment name. Otherwise,
you can use the browser to choose an object
```

Add the following to the arguments:

```
--input ${input} --find_string ${find_string} --replace_string ${replace_string} --column ${column} --output ${output} --coalesce ${coalesce}
```
<b>input</b> points to the input data source. <b>find_string</b> refers to the string to be searched for(demonstrated below with single quotes) and
<b>replace_string</b> refers to the replaced string in <b>column</b>(s).


```
Specify path in Object Storage to store logs. These may be useful later for troubleshooting.
```
![image info](./utils/P6.png)


```
Click "Save changes" to save the Application
```


