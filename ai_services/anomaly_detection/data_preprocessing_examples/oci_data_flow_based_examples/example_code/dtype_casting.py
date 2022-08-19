from pyspark.sql import SparkSession
import argparse


def create_spark_session(session_name):
    """
    Create a Spark session
    Args:
        session_name: name to be assigned to the spark session
    Return:
        a spark session
    """
    spark_session = SparkSession.builder.appName(session_name).getOrCreate()
    return spark_session


def get_dtype(df, column):
    """
    Get data type for a column
    Args:
        df: input dataframe
        column: column to return data type for

    Return:
        data type of a selected column
    """

    return [dtype for name, dtype in df.dtypes if name == column][0]


def cast_data_type(df, column, dtype):
    """
    Apply type casting to a column of input dataframe
    Args:
        df: input dataframe
        column: column to apply data type casting
        dtype: desired data type

    Return:
        dataframe with data type casting applied to selected column
    """

    df = df.withColumn(column, df[column].cast(dtype))
    assert get_dtype(df, column) == dtype
    return df


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--column", required=True)
    parser.add_argument("--dtype", required=True)
    parser.add_argument("--coalesce", required=False, action="store_true")
    args = parser.parse_args()

    spark = create_spark_session("pyspark_dtype_casting")
    input_data = spark.read.csv(args.input, sep=",", inferSchema=False, header=True)

    df = cast_data_type(input_data, args.column, args.dtype)

    if args.coalesce:
        df.coalesce(1).write.csv(args.output, header=True)
    else:
        df.write.csv(args.output, header=True)


if __name__ == "__main__":
    main()
