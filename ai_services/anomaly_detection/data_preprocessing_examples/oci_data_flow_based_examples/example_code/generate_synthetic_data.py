from pyspark.sql import SparkSession
import argparse
from pyspark.sql import functions as F
from pyspark.mllib.random import RandomRDDs
import numpy as np
import pandas as pd
import string
import random
from pyspark.sql.types import StringType


def create_spark_session():
    spark_session = SparkSession.builder.appName(
        "PySpark_synthetic_data_generator"
    ).getOrCreate()
    return spark_session


def gen_synthetic_pivot(spark, args):
    """
    Generate a dataset with three columns as timestamp, signal ID and signal value
    and num_signals x num_observations rows,
    the number of observations per signals are identical
    Args:
        spark: Spark session
        args: contains
            args.output: destination directory to store generated sample_datasets as a CSV file
            args.num_signals: number of signals
            args.num_observations: number of observations
            args.freq: sampling interval for time series
        max_cat: maximum number of categories in each signal/ column
    """
    datetime = pd.date_range(
        start="1/1/2018", periods=args.num_observations, freq=args.freq
    )
    rdd = spark.sparkContext.parallelize(range(args.num_signals)).flatMap(
        lambda x: [
            (
                str(dt),
                f"meter-{x}",
                np.random.rand(),
            )
            + tuple(map(str, np.random.randint(3, size=args.max_pivot - 1)))
            for dt in datetime
        ]
    )
    df = rdd.toDF(
        ["timestamp", "meter-ID", "value"]
        + [f"dim{i+1}" for i in range(args.max_pivot - 1)]
    )
    # df = df.orderBy(F.rand())
    df.coalesce(1).write.csv(args.output + "/pivot", header=True)


def gen_synthetic_catvar(spark, args, max_cat=4):
    """
    Generate a dataset of all categorical variables
    Args:
        spark: Spark session
        args: contains
            args.output: destination directory to store generated sample_datasets as a CSV file
            args.num_signals: number of signals
            args.num_observations: number of observations
            args.freq: sampling interval for time series
        max_cat: maximum number of categories in each signal/ column
    """
    if max_cat < 2:
        raise ValueError("num of categories should be  >= 2")
    # catvar_cols = [("", rs.randint(max_cat)) for i in range(n_cols)]
    catvar_cols = [("", max_cat) for i in range(args.num_signals)]
    datetime = pd.date_range(
        start="1/1/2018", periods=args.num_observations, freq=args.freq
    )

    data = [{"timestamp": str(dt)} for dt in datetime]
    df = spark.createDataFrame(data)

    select_statement = []
    for k, (_, n_cat) in enumerate(catvar_cols):
        select_statement.append(
            F.array([F.lit(i) for i in range(n_cat)])
            .getItem((F.rand() * n_cat).cast("int"))
            .alias(f"feat{k}")
        )
    df = df.select(*df.columns, *select_statement)
    df.coalesce(1).write.csv(args.output + "/catvar", header=True)


def gen_synthetic_uniform(spark, args):
    """
    Generate a dataset of random values uniformly distributed in [0, 1]
    Args:
        spark: Spark session
        args: contains
            args.output: destination directory to store generated sample_datasets as a CSV file
            args.num_signals: number of signals
            args.num_observations: number of observations
            args.frac_nan: percentage of nan observations in each signal/ column
            args.freq: sampling interval for time series

    """
    if args.frac_nan > 1 or args.frac_nan < 0:
        raise ValueError("Invalid range for frac_nan")

    def inject_nan():
        x = np.random.rand()
        return x if x > args.frac_nan else np.nan

    datetime = pd.date_range(
        start="1/1/2018", periods=args.num_observations, freq=args.freq
    )
    columns = ["timestamp"] + [f"feat{i + int(args.offset)}" for i in range(args.num_signals)]
    df = (
        spark.sparkContext.parallelize(range(args.num_observations))
        .map(
            lambda x: (str(datetime[x]),)
            + tuple(inject_nan() for _ in range(args.num_signals))
        )
        .toDF(columns)
    )

    df.coalesce(1).write.csv(args.output + "/uniform", header=True)


def gen_synthetic_string(spark, args):
    """
    Generate a dataset of all string variables with PATTERN in their name
    Args:
        spark: Spark session
        args: contains
            args.output: destination directory to store generated sample_datasets as a CSV file
            args.num_signals: number of signals
            args.num_observations: number of observations
            args.freq: sampling interval for time series
    """

    def randomString(length):
        letters = string.ascii_letters
        result_str = "".join(random.choice(letters) for i in range(length))
        return result_str

    datetime = pd.date_range(
        start="1/1/2018", periods=args.num_observations, freq=args.freq
    )

    columns = ["timestamp"] + [f"feat{i}" for i in range(args.num_signals)]
    df = (
        spark.sparkContext.parallelize(range(args.num_observations))
        .map(
            lambda x: (str(datetime[x]),)
            + tuple(
                randomString(np.random.randint(5))
                + "PATTERN"
                + randomString(np.random.randint(5))
                for _ in range(args.num_signals)
            )
        )
        .toDF(columns)
    )

    df.coalesce(1).write.csv(args.output + "/string", header=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--dataset", required=False)
    parser.add_argument("--num_signals", required=True, type=int)
    parser.add_argument("--num_observations", required=True, type=int)
    parser.add_argument("--freq", required=False, default="1min")
    parser.add_argument("--frac_nan", required=False, type=float)
    parser.add_argument("--offset", required=False, type=int, default=0)
    parser.add_argument("--max_pivot", required=False, type=int)
    args = parser.parse_args()

    spark_session = create_spark_session()

    if args.dataset == "catvar":
        gen_synthetic_catvar(spark_session, args)
    elif args.dataset == "uniform":
        gen_synthetic_uniform(spark_session, args)
    elif args.dataset == "string":
        gen_synthetic_string(spark_session, args)
    elif args.dataset == "pivot":
        gen_synthetic_pivot(spark_session, args)
    else:
        gen_synthetic_catvar(spark_session, args)
        gen_synthetic_uniform(spark_session, args)
        gen_synthetic_string(spark_session, args)
        gen_synthetic_pivot(spark_session, args)


if __name__ == "__main__":
    main()
