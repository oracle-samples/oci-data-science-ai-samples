import argparse
from pyspark.sql import SparkSession
import pyspark.sql.functions as F
from pyspark.sql.window import Window


def windowing(df, batch_size):
    """
    Args:
        df: dataframe to perform windowing on
        batch_size: number of rows per batch
    """
    if "timestamp" not in df.columns:
        raise ValueError("timestamp column not found!")
    df = df.withColumn("timestamp_1", F.unix_timestamp(F.col("timestamp")))
    window_spec = Window.orderBy("timestamp_1")
    return df.withColumn(
        "batch_id",
        F.floor(
            (F.row_number().over(window_spec) - F.lit(1)) / int(batch_size)
        ),
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--batch_size", required=True)
    args = parser.parse_args()

    spark = SparkSession.builder.appName("DataFlow").getOrCreate()
    df = spark.read.csv(args.input, header=True)
    df = windowing(df, args.batch_size)
    df.repartition("batch_id").write.partitionBy(
        "batch_id").mode("overwrite").format("csv").save(args.output)
