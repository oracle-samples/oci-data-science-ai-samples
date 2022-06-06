import argparse
from pyspark.sql import SparkSession

def main(args):
    spark = SparkSession.builder.appName("DataFlow").getOrCreate()
    df = spark.read.csv(args.input, header=True)
    columns_to_remove = args.columns_to_remove.split(',')
    cols = ()
    for col in columns_to_remove:
        cols += (col,)
    df = df.drop(*cols)

    if args.coalesce:
        df.coalesce(1).write.csv(args.output, header=True)
    else:
        df.write.csv(args.output, header=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--columns_to_remove", required=True)
    parser.add_argument("--coalesce", required=False, action="store_true")

    args = parser.parse_args()
    main(args)