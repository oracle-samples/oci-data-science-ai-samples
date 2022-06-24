# Prepackaged DF: one way to hook up multiple components

## Use case
You have already known that OCI Data Flow is a powerful service for running Spark applications, but one problem is that it will allow you to upload only one application (code) file per application. This may force you to white all the logics in one file, which is bad for mid-large scale applications where modularization is desired.

In consideration of this, Data Flow allows you to upload an archive of multiple code files as a third-party library. We will show how to do it step by step in this guide.

## Reference
For a more general and comprehensive introduction on adding dependency to Data Flow in different languages under various OS, please check their [official doc](https://docs.oracle.com/en-us/iaas/data-flow/using/third-party-libraries.htm#example-requirements-packages). Here we are using **MacOS**, and we will use Python and code samples under `example_code` as demo.

## Steps
### Building up Python Wheel
Python .whl files, or wheels, is a popular tooling for building for Python packages. If you’ve installed a Python package using pip, then chances are that package is built with wheel.

Here we will wrap up everything inside `example_code` as our dependency package. Firstly go to the right path:
```
$ cd <path-to-your-workspace>/oci-data-science-ai-samples/ai_services/anomaly_detection/data_preprocessing_examples/oci_data_flow_based_examples
```

Create a `virtualenv` for creating lightweight virtual environments with their own site directories, optionally isolated from system site directories:
```
$ pip install virtualenv
$ virtualenv venv
$ . venv/bin/activate
```

Install `setuptools` and `wheel` if you haven't already:
```
$ pip install wheel setuptools
```

Create the following `setup.py`:
```
from setuptools import setup

setup(
    name='prepackaged_df',
    version='1.0',
    packages=['example_code']
)
```
Basically this is how your current folder should look like this:
```
|- example_code
|- venv
|- setup.py
|- <other files>
```

Now, type the following command to build the wheel:
```
python setup.py bdist_wheel
```
Once it's done, you should see now your folder contains:
```
|- example_code
|- venv
|- setup.py
|- prepackaged_df.egg-info
|- build
|- dist
    |- prepackaged_df-1.0-py3-none-any.whl
|- <other files>
```
Yes, your `prepackaged_df-1.0-py3-none-any.whl` is successfully built under `dist`. Go to `dist` and install the packager tool image:
```
$ cd dist
$ docker pull phx.ocir.io/oracle/dataflow/dependency-packager:latest
```
Create the following `requirements.txt`:
```
-i https://pypi.org/simple
/opt/dataflow/prepackaged_df-1.0-py3-none-any.whl
```
Use docker container to create the archive:
```
$ docker run --rm -v $(pwd):/opt/dataflow --pull always -it phx.ocir.io/oracle/dataflow/dependency-packager:latest -p 3.6
```
After some time, you should see your `archive.zip` is successfully. Now the folder structure will be look like:
```
|- example_code
|- venv
|- setup.py
|- prepackaged_df.egg-info
|- build
|- dist
    |- prepackaged_df-1.0-py3-none-any.whl
    |- archive.zip
    |- requirements.txt
    |- <other files>
|- <other files>
```
Cool! Now you are ready to use your package for writing application. The following is an example of utilizing [remove_unnecessary_columns](./example_code/remove_unnecessary_columns.py):
```
import argparse
from pyspark.sql import SparkSession
from example_code import remove_unnecessary_columns

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--columns_to_remove", required=True)
    parser.add_argument("--coalesce", required=False, action="store_true")

    args = parser.parse_args()
    spark = SparkSession.builder.appName("DataFlow").getOrCreate()
    df = spark.read.csv(args.input, header=True)
    df = remove_unnecessary_columns.remove_unnecessary_columns(df, args.columns_to_remove)

    if args.coalesce:
        df.coalesce(1).write.csv(args.output, header=True)
    else:
        df.write.csv(args.output, header=True)
```
Let's call it `test_remove_unnecessary_columns.py`. Now you have everything ready, and follow all the steps same to other DF applications. The only thing different is you need to upload the `archive.zip` to one of your object storage bucket and import it under `Archive URI`:

![](./utils/prepackaged.png)
