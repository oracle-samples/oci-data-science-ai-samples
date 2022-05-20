import argparse
from pyspark.sql import SparkSession
import pyspark.sql.functions as F


def main(args):
    spark = SparkSession.builder.appName("DataFlow").getOrCreate()
    df = spark.read.load(
        args.input, format="csv", sep=",", inferSchema="true", header="true"
    )
    df = df.select(*df.columns, F.monotonically_increasing_id().alias("idx"))
    df = df.filter(df.idx % int(args.window_size) == 0)
    df = df.drop(F.col("idx"))

    if args.coalesce:
        df.coalesce(1).write.csv(args.output, header=True)
    else:
        df.write.csv(args.output, header=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--window_size", required=True)
    parser.add_argument("--coalesce", required=False, action="store_true")

    args = parser.parse_args()
    main(args)
