import argparse
from pyspark.sql import SparkSession
from pyspark.sql.functions import rand
from pyspark.sql.functions import lit


def add_synthetic_column(df, **kwargs):
    if "valueGenerator" not in kwargs:
        raise ValueError("Generator not specified for values! Pass valueGenerator=constant or random")
    if "columnName" not in kwargs:
        raise ValueError("Column name argument not specified! Pass columnName=<foo>")
    if kwargs["valueGenerator"] == "constant":
        if "value" not in kwargs:
            raise ValueError("Value needs to be specified for constant valued columns! Pass \"value\"=\"<123>\"")
        df = df.withColumn(kwargs["columnName"], lit(kwargs["value"]))
    elif kwargs["valueGenerator"] == "random":
        df = df.withColumn(kwargs["columnName"], rand())
    else:
        raise ValueError(f"Invalid generator {kwargs['valueGenerator']}! Pass valueGenerator=constant or random")
    return df

if __name__ == '__main__':
    args = argparse.ArgumentParser()
    args.add_argument("--input", required=True)
    args.add_argument("--output", required=True)
    args.add_argument("--valueGenerator", required=True)
    args.add_argument("--columnName", required=True)
    args.add_argument("--value", required=False)
    args = args.parse_args()
    spark = SparkSession.builder.appName("PySpark_Sharding").getOrCreate()
    df_input = spark.read.load(
        args.input, format="csv", sep=",", inferSchema="true", header="true"
    )
    df1 = add_synthetic_column(df_input, **vars(args))
    df1.coalesce(1).write.csv(args.output, header=True)
