from pyspark.sql import SparkSession
import argparse
import pandas as pd
import numpy as np
from pyspark.sql import functions as F


class ParseKwargs(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        values = values[0].split(" ") if len(values) == 1 else values
        if ":" not in values[0]:
            setattr(namespace, self.dest, values)
        else:
            setattr(namespace, self.dest, dict())
            for value in values:
                key, value = value.split(":")
                getattr(namespace, self.dest)[key] = value


def spark_pivoting(spark, filepath, groupby, pivot, agg):
    """
    Pivot Operation
    Args:
        spark: Spark session
        filepath: path to input CSV file
        groupby: dimensions to groupby into summary rows
        pivot: pivot column - rows of which to be converted into columns
        agg:  a dictionary where key = <column name> and value = <aggregation function>
    """
    data = spark.read.load(
        filepath, format="csv", sep=",", inferSchema="true", header="true"
    )
    if not "timestamp" in data.columns:
        raise ValueError("timestamp column not found!")
    return data.groupBy(groupby).pivot(pivot).agg(agg)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--pivot", required=True)
    parser.add_argument("--groupby", nargs="*", required=True, action=ParseKwargs)
    parser.add_argument("--agg", nargs="*", required=True, action=ParseKwargs)
    parser.add_argument("--coalesce", required=False, action="store_true")
    args = parser.parse_args()

    spark = SparkSession.builder.appName("PySpark_pivoting").getOrCreate()
    spark.conf.set("spark.sql.pivotMaxValues", "1000000")

    df_pivot = spark_pivoting(
        spark,
        filepath=args.input,
        groupby=args.groupby,
        pivot=args.pivot,
        agg=args.agg,
    )
    if args.coalesce:
        df_pivot.coalesce(1).write.csv(args.output, header=True)
    else:
        df_pivot.write.csv(args.output, header=True)


if __name__ == "__main__":
    main()
