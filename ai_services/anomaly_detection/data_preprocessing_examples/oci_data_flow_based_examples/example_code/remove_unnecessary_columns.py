# Copyright © 2021, Oracle and/or its affiliates.

import argparse
from pyspark.sql import SparkSession


def remove_unnecessary_columns(df, columns_to_remove):
    columns_to_remove_arr = columns_to_remove.split(',')
    cols = ()
    for col in columns_to_remove_arr:
        cols += (col,)
    return df.drop(*cols)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--columns_to_remove", required=True)
    parser.add_argument("--coalesce", required=False, action="store_true")

    args = parser.parse_args()
    spark = SparkSession.builder.appName("DataFlow").getOrCreate()
    df = spark.read.csv(args.input, header=True)
    df = remove_unnecessary_columns(df, args.columns_to_remove)

    if args.coalesce:
        df.coalesce(1).write.csv(args.output, header=True)
    else:
        df.write.csv(args.output, header=True)
