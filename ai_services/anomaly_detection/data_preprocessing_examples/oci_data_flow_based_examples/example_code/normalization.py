from pyspark.sql import SparkSession
from pyspark.sql import functions as F
import argparse
from pyspark.ml.feature import MinMaxScaler, StandardScaler, VectorAssembler


def extract(row):
    return (row.id,) + tuple(row.scaledFeatures.toArray().tolist()[:-1])


def normalize_data(df, scaler_type, columns):
    """
    Scale numeric features using two methods
        1) minmax normalization or
        2) standardization
    Args:
        df: input dataframe
        scaler_type: either "minmax" or "standard"
        columns: columns to be scaled/ normalized

    Return:
        Scaled dataframe
    """
    columns = (
        [col for col in df.columns if col not in {"id", "timestamp"}]
        if not columns
        else columns
    )
    not_normalized_columns = list(set(df.columns).difference(set(columns)))
    df = df.withColumn("id", F.monotonically_increasing_id())
    columns += ["id"]
    not_normalized_columns += ["id"]
    assembler = VectorAssembler().setInputCols(
        columns).setOutputCol("features")
    transformed = assembler.transform(df.select(columns))
    if scaler_type == "minmax":
        scaler = MinMaxScaler(inputCol="features", outputCol="scaledFeatures")
    elif scaler_type == "standard":
        scaler = StandardScaler(
            inputCol="features",
            outputCol="scaledFeatures")
    else:
        raise ValueError("Invalid scaler type")
    scalerModel = scaler.fit(transformed.select("features"))
    scaledData = scalerModel.transform(transformed)
    scaledData = (
        scaledData.select(["id", "scaledFeatures"])
        .rdd.map(extract)
        .toDF(["id"] + columns[:-1])
    )

    return df.select(not_normalized_columns).join(
        scaledData,
        on="id").drop("id")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--norm", required=True)
    parser.add_argument("--columns", nargs="+", required=True)
    parser.add_argument("--coalesce", required=False, action="store_true")
    args = parser.parse_args()
    columns = args.columns[0].split(
        " ") if len(args.columns) == 1 else args.columns

    spark = SparkSession.builder.appName("DataFlow").getOrCreate()
    input_data = spark.read.csv(
        args.input,
        sep=",",
        inferSchema=True,
        header=True)
    input_data_scaled = normalize_data(input_data, args.norm, columns)

    if args.coalesce:
        input_data_scaled.coalesce(1).write.csv(args.output, header=True)
    else:
        input_data_scaled.write.csv(args.output, header=True)
