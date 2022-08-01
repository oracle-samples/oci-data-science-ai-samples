import argparse
from pyspark.sql import SparkSession


def distinct_category_extract(df, **kwargs):
    category = kwargs["category"]

    distinct_categories = list(
        df.select(category).distinct().toPandas()[category])
    res = ' '.join(str(x) for x in distinct_categories)
    return res


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--category", required=True)
    args = parser.parse_args()

    spark = SparkSession.builder.appName(
        "PySpark_OneHotEncodingPreparer").getOrCreate()
    df = spark.read.load(
        args.input, format="csv", sep=",", inferSchema="true", header="true"
    )

    print(distinct_category_extract(df, **vars(args)))
