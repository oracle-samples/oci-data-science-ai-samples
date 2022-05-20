from pyspark.sql import SparkSession
from pyspark.sql import functions as F
import argparse


def create_spark_session(session_name):
    """
    Create a Spark session
    Args:
        session_name: name to be assigned to the spark session
    Return:
        a spark session
    """
    spark_session = SparkSession.builder.appName(session_name).getOrCreate()
    return spark_session


def get_nan_count(df):
    """
    Count Null values in a dataframe
    Args:
        df: input dataframe

    Return:
        the number of Null values in each column
    """
    return df.select(
        [
            F.count(F.when(F.isnan(c) | F.col(c).isNull(), c)).alias(c) / df.count()
            for c in df.columns
        ]
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--coalesce", required=False, action="store_true")
    args = parser.parse_args()

    spark = create_spark_session("pySpark_percentage_of_nulls")
    input_data = spark.read.csv(args.input, sep=",", inferSchema=False, header=True)

    df = get_nan_count(input_data)

    if args.coalesce:
        df.coalesce(1).write.csv(args.output, header=True)
    else:
        df.write.csv(args.output, header=True)


if __name__ == "__main__":
    main()
