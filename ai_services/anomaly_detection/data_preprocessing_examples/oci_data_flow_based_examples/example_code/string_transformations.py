# Copyright © 2021, Oracle and/or its affiliates.
# The Universal Permissive License (UPL),
# Version 1.0 as shown at https://oss.oracle.com/licenses/upl.

import argparse

from pyspark.sql import SparkSession
from pyspark.sql.functions import regexp_replace


class parse_kwargs(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        values = values[0].split(" ") if len(values) == 1 else values
        if ":" not in values[0]:
            setattr(namespace, self.dest, values)
        else:
            setattr(namespace, self.dest, dict())
            for value in values:
                key, value = value.split(":")
                getattr(namespace, self.dest)[key] = value


def string_transformation(df, find_string, replace_string, column):
    columns_to_replace = column if column else df.columns
    for col in columns_to_replace:
        df = df.withColumn(
            col,
            regexp_replace(col, find_string, replace_string))
    return df


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--find_string", required=True)
    parser.add_argument("--replace_string", required=True)
    parser.add_argument(
        "--column",
        nargs="*",
        required=False,
        action=parse_kwargs)
    parser.add_argument("--output", required=True)
    parser.add_argument("--coalesce", required=False, action="store_true")

    args = parser.parse_args()

    spark = SparkSession.builder.appName("DataFlow").getOrCreate()
    df = spark.read.load(
        args.input, format="csv", sep=",", inferSchema="true", header="true"
    )

    df = string_transformation(
        df,
        find_string=args.find_string,
        replace_string=args.replace_string,
        column=args.column
    )

    if args.coalesce:
        df.coalesce(1).write.csv(args.output, header=True)
    else:
        df.write.csv(args.output, header=True)
