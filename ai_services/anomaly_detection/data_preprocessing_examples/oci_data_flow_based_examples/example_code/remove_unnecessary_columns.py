import argparse
from pyspark.sql import SparkSession


def remove_unnecessary_columns(input, columns_to_remove, output, coalesce):
    spark = SparkSession.builder.appName("DataFlow").getOrCreate()
    df = spark.read.csv(input, header=True)
    columns_to_remove_arr = columns_to_remove.split(',')
    cols = ()
    for col in columns_to_remove_arr:
        cols += (col,)
    df = df.drop(*cols)

    if coalesce:
        df.coalesce(1).write.csv(output, header=True)
    else:
        df.write.csv(args.output, header=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--columns_to_remove", required=True)
    parser.add_argument("--coalesce", required=False, action="store_true")

    args = parser.parse_args()
    remove_unnecessary_columns(args.input, args.columns_to_remove,
                               args.output, args.coalesce)
