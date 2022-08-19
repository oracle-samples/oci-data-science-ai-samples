import argparse

from pyspark.sql import SparkSession
from pyspark.sql.functions import when


def one_hot_encoding(df, category):
    distinct_values = df.select(category).distinct().collect()
    for value in distinct_values:
        category_value = value[category]
        df = df.withColumn(
            'is_' + str(category_value),
            when(
                df[category] == category_value, 1
            )
            .otherwise(0)
        )
    return df.drop(category)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--category", required=True)
    parser.add_argument("--coalesce", required=False, action="store_true")
    args = parser.parse_args()

    spark = SparkSession.builder.appName(
        "PySpark_OneHotEncoding").getOrCreate()
    df_input = spark.read.load(
        args.input, format="csv", sep=",", inferSchema="true", header="true"
    )
    df_output = one_hot_encoding(df_input, category=args.category)
    if args.coalesce:
        df_output.coalesce(1).write.csv(args.output, header=True)
    else:
        df_output.write.csv(args.output, header=True)
