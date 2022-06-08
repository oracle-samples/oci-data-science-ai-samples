import argparse
from pyspark.sql import SparkSession
import pyspark.sql.functions as F
from pyspark.sql.window import Window


def windowing(df, batch_size, dest_dir):
    """
    Args:
        df: dataframe to perform windowing on
        batch_size: number of rows per batch
        dest_dir: directory where output will be stored
    """
    if "timestamp" not in df.columns:
        raise ValueError("timestamp column not found!")
    df = df.withColumn("timestamp_1", F.unix_timestamp(F.col("timestamp")))
    window_spec = Window.orderBy("timestamp_1")
    df = df.withColumn(
        "batch_id",
        F.floor((F.row_number().over(window_spec) - F.lit(1)) / int(batch_size)),
    )
    df.repartition("batch_id").write.partitionBy("batch_id").mode("overwrite").format(
        "csv"
    ).save(dest_dir)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--batch_size", required=True)
    args = parser.parse_args()

    spark = SparkSession.builder.appName("DataFlow").getOrCreate()
    df = spark.read.csv(args.input, header=True)
    windowing(df, args.batch_size, args.output)


if __name__ == "__main__":
    main()
