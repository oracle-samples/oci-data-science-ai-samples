import argparse

from pyspark.sql import SparkSession
from pyspark.sql.functions import when


class parse_kwargs(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        values = values[0].split(" ") if len(values) == 1 else values
        if ":" not in values[0]:
            setattr(namespace, self.dest, values)
        else:
            setattr(namespace, self.dest, dict())
            for value in values:
                key, value = value.split(":")
                getattr(namespace, self.dest)[key] = value


def one_hot_encoding(df, **kwargs):
    category = kwargs["category"]

    distinct_categories = None
    if ('distinct_categories' not in kwargs or
            kwargs['distinct_categories'] is None):
        distinct_categories = list(
            df.select(category).distinct().toPandas()[category])
    else:
        distinct_categories = kwargs["distinct_categories"]
        if isinstance(distinct_categories, str):
            distinct_categories = distinct_categories.split()

    for value in distinct_categories:
        df = df.withColumn(
            'is_' + str(value),
            when(
                df[category] == value, 1
            )
            .otherwise(0)
        )
    return distinct_categories, df.drop(category)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--category", required=True)
    parser.add_argument(
        "--distinct_categories",
        nargs="+",
        required=False,
        action=parse_kwargs)
    parser.add_argument("--coalesce", required=False, action="store_true")
    args = parser.parse_args()

    spark = SparkSession.builder.appName(
        "PySpark_OneHotEncoding").getOrCreate()
    df_input = spark.read.load(
        args.input, format="csv", sep=",", inferSchema="true", header="true"
    )
    _, df_output = one_hot_encoding(df_input, **vars(args))

    if args.coalesce:
        df_output.coalesce(1).write.csv(args.output, header=True)
    else:
        df_output.write.csv(args.output, header=True)
