from pyspark.sql import SparkSession
from pyspark.sql import functions as F
import argparse


def __create_spark_session(session_name):
    """
    Create a Spark session
    Args:
        session_name: name to be assigned to the spark session
    Return:
        a spark session
    """
    spark_session = SparkSession.builder.appName(session_name).getOrCreate()
    return spark_session


def format_timestamp(df):
    """
    Reformat timestamps to ISO 8601
    Args:
        df: input dataframe

    Return:
        input dataframe with timestamps formatted as ISO 8601
    """
    return df.withColumn(
        "timestamp",
        F.date_format(
            F.to_timestamp("timestamp"), "yyyy-MM-dd'T'HH:mm:ss'Z'").cast(
            "string"
        ),
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--coalesce", required=False, action="store_true")
    args = parser.parse_args()

    spark = __create_spark_session("pyspark_timestamp_formatting")
    input_data = spark.read.csv(
        args.input,
        sep=",",
        inferSchema=False,
        header=True)

    df = format_timestamp(input_data)

    if args.coalesce:
        df.coalesce(1).write.csv(args.output, header=True)
    else:
        df.write.csv(args.output, header=True)
