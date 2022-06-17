# Copyright © 2021, Oracle and/or its affiliates.

import argparse
import os

from pyspark import SparkConf
from pyspark.sql import SparkSession, Window
import pyspark.sql.functions


def aggregation(dataframe, aggregation_function, window_size, step_size):
    grouping_functions = ["avg", "sum", "min", "max"]
    if aggregation_function in grouping_functions:
        if "timestamp" not in dataframe.columns:
            raise ValueError("timestamp column not found!")
        w = Window.orderBy('timestamp').rowsBetween(0, int(window_size))
        signals = dataframe.columns.copy()
        signals.remove('timestamp')
        method = getattr(pyspark.sql.functions, aggregation_function)
        dataframe = dataframe.select(
            'timestamp', *(method(column).over(w) for column in signals),
            pyspark.sql.functions.monotonically_increasing_id().alias("idx"))
    elif aggregation_function == "first":
        dataframe = dataframe.withColumn(
            "idx",
            pyspark.sql.functions.monotonically_increasing_id()
        )
    else:
        raise ValueError(
            "aggregation_function should be one of avg, sum. min, max or first"
        )
    dataframe = dataframe.filter(dataframe.idx % int(step_size) == 0)

    return dataframe.drop("idx")


def __get_dataflow_spark_session(
        app_name="DataFlow",
        file_location=None,
        profile_name=None,
        spark_config={}
):
    """
    Get a Spark session in a way that supports running locally or in Data Flow.
    """
    if in_dataflow():
        spark = SparkSession.builder.appName(app_name)
    else:
        # Import OCI.
        try:
            import oci
        except Exception as e:
            print(f'Exception: {e}')
            raise Exception(
                "You need to install the OCI python library to test locally"
            )

        # Use defaults for anything unset.
        if file_location is None:
            file_location = oci.config.DEFAULT_LOCATION
        if profile_name is None:
            profile_name = oci.config.DEFAULT_PROFILE

        # Load the config file.
        try:
            oci_config = oci.config.from_file(
                file_location=file_location, profile_name=profile_name
            )
        except Exception as e:
            print("You need to set up your OCI config properly to run locally")
            raise e
        conf = SparkConf()
        conf.set("fs.oci.client.auth.tenantId", oci_config["tenancy"])
        conf.set("fs.oci.client.auth.userId", oci_config["user"])
        conf.set("fs.oci.client.auth.fingerprint", oci_config["fingerprint"])
        conf.set("fs.oci.client.auth.pemfilepath", oci_config["key_file"])
        conf.set(
            "fs.oci.client.hostname",
            f'https://objectstorage.{oci_config["region"]}.oraclecloud.com',
        )
        spark = SparkSession.builder.appName(app_name).config(conf=conf)

    # Add in extra configuration.
    for key, val in spark_config.items():
        spark.config(key, val)

    # Create the Spark session.
    session = spark.getOrCreate()
    return session


def in_dataflow():
    """
    Determine if we are running in OCI Data Flow by checking the environment.
    """
    if os.environ.get("HOME") == "/home/dataflow":
        return True
    return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--window_size", required=True)
    parser.add_argument("--step_size", required=True)
    parser.add_argument(
        "--aggregation_function",
        required=False,
        default="avg")
    parser.add_argument("--coalesce", required=False, action="store_true")
    args = parser.parse_args()
    spark = __get_dataflow_spark_session()
    df = spark.read.csv(args.input, header=True)
    df = aggregation(
        df,
        args.aggregation_function,
        args.window_size,
        args.step_size)

    if args.coalesce:
        df.coalesce(1).write.csv(args.output, header=True)
    else:
        df.write.csv(args.output, header=True)
