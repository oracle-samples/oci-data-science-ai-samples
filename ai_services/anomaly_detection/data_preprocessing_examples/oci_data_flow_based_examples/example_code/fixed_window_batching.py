import argparse
from pyspark.sql import SparkSession
import pyspark.sql.functions as F


def main(args):
    spark = SparkSession.builder.appName("DataFlow").getOrCreate()
    df = spark.read.csv(args.input, header=True)
    df = df.withColumn("id", F.monotonically_increasing_id())
    df = df.withColumn("id_tmp", F.floor(F.col("id") / int(args.batch_size))).orderBy("id_tmp")
    df.drop("id")
    df.repartition("id_tmp").write.partitionBy("id_tmp").mode("overwrite").format("csv").save(args.output)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--batch_size", required=True)

    args = parser.parse_args()
    main(args)
