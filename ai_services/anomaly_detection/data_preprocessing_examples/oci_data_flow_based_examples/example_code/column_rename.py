import argparse
from pyspark.sql import SparkSession


def main(args):
    spark = SparkSession.builder.appName("DataFlow").getOrCreate()
    df = spark.read.csv(args.input, header=True)
    df = df.withColumnRenamed(args.original_column, args.renamed_column)

    if args.coalesce:
        df.coalesce(1).write.csv(args.output, header=True)
    else:
        df.write.csv(args.output, header=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--original_column", required=True)
    parser.add_argument("--renamed_column", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--coalesce", required=False, action="store_true")

    args = parser.parse_args()
    main(args)
