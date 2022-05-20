from pyspark.sql import SparkSession
import argparse
import pandas as pd
import numpy as np
from pyspark.sql import functions as F


def spark_pivoting(spark, filepath, groupby_col, pivot_col, agg_col):
    """
    Pivot Operation
    Args:
        spark: Spark session
        filepath: path to input CSV file
        groupby_col: dimensions to groupby into summary rows
        pivot_col: pivot column - rows of which to be converted into columns
        agg_col: aggregation column
    """
    max_pivot = len(groupby_col)
    data = spark.read.load(
        filepath, format="csv", sep=",", inferSchema="true", header="true"
    )
    if not "timestamp" in data.columns:
        raise ValueError("timestamp column not found!")

    return data.groupBy(groupby_col).pivot(pivot_col).avg(agg_col)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=False)
    parser.add_argument("--pivot", required=True)
    parser.add_argument("--groupby", nargs="+", required=True)
    parser.add_argument("--agg", required=True)
    parser.add_argument("--coalesce", required=False, action="store_true")
    args = parser.parse_args()

    spark = SparkSession.builder.appName("PySpark_pivoting").getOrCreate()
    spark.conf.set("spark.sql.pivotMaxValues", "1000000")

    groupby = args.groupby[0].split(" ") if len(args.groupby) == 1 else args.groupby

    df_pivot = spark_pivoting(
        spark,
        filepath=args.input,
        groupby_col=groupby,
        pivot_col=args.pivot,
        agg_col=args.agg,
    )
    if args.coalesce:
        df_pivot.coalesce(1).write.csv(args.output, header=True)
    else:
        df_pivot.write.csv(args.output, header=True)


if __name__ == "__main__":
    main()
