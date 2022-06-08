# Copyright © 2021, Oracle and/or its affiliates.

import argparse
import os

from pyspark import SparkConf
from pyspark.sql import SparkSession


def main(args):
    spark = get_dataflow_spark_session()
    df1 = spark.read.csv(args.input1, header=True)
    df2 = spark.read.csv(args.input2, header=True)
    df1 = df1.unionByName(df2)
    df1 = df1.sort("timestamp")
    df1 = df1.dropDuplicates(["timestamp"])
    if args.coalesce:
        df1.coalesce(1).write.csv(args.output, header=True)
    else:
        df1.write.csv(args.output, header=True)


def get_dataflow_spark_session(
    app_name="DataFlow", file_location=None, profile_name=None, spark_config={}
):
    """
    Get a Spark session in a way that supports running locally or in Data Flow.
    """
    if in_dataflow():
        spark_builder = SparkSession.builder.appName(app_name)
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
        spark_builder = SparkSession.builder.appName(app_name).config(conf=conf)

    # Add in extra configuration.
    for key, val in spark_config.items():
        spark_builder.config(key, val)

    # Create the Spark session.
    session = spark_builder.getOrCreate()
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
    parser.add_argument("--input1", required=True)
    parser.add_argument("--input2", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--coalesce",  required=False, action="store_true")

    args = parser.parse_args()
    main(args)