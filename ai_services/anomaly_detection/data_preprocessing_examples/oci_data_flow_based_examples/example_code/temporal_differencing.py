from pyspark.sql import SparkSession
import argparse
from pyspark.sql import Window
import pyspark.sql.functions as F


def temporal_differencing(df, diff_factor, output, coalesce):
    lagWindow = Window.rowsBetween(diff_factor, 0)
    for col in df.columns:
        if col != "timestamp":
            df = df.withColumn(col,
                               df[col] - F.first(df[col]).over(lagWindow))

    if coalesce:
        df.coalesce(1).write.csv(output, header=True)
    else:
        df.write.csv(output, header=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--diff_factor", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--coalesce", required=False, action="store_true")

    args = parser.parse_args()

    spark = SparkSession.builder.appName("DataFlow").getOrCreate()
    df = spark.read.load(
        args.input, format="csv", sep=",", inferSchema="true", header="true"
    )
    temporal_differencing(
        df,
        diff_factor=args.diff_factor,
        output=args.output,
        coalesce=args.coalesce
    )


if __name__ == "__main__":
    main()
