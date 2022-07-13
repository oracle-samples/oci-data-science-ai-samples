import argparse
from pyspark.sql import SparkSession


def column_rename(df, **kwargs):
    df = df.withColumnRenamed(
        kwargs["original_column"], kwargs["renamed_column"])
    return df


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--original_column", required=True)
    parser.add_argument("--renamed_column", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--coalesce", required=False, action="store_true")

    args = parser.parse_args()
    spark = SparkSession.builder.appName("DataFlow").getOrCreate()
    df = spark.read.csv(args.input, header=True)

    df_rename = column_rename(df, **vars(args))

    if args.coalesce:
        df_rename.coalesce(1).write.csv(args.output, header=True)
    else:
        df_rename.write.csv(args.output, header=True)
