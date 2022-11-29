from pyspark.sql import SparkSession
from pyspark.sql import functions as F
import argparse
from datetime import datetime

MAX_NUM_COL = 300
MAX_DATAPOINTS = 100


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


def is_null(df, column):
    return df.filter(F.col(column).isNull() | F.isnan(column)).count() > 0


def is_duplicate(df, columns):
    return df.count() > df.dropDuplicates(columns).count()


def valid_dtype(df, column, target_dtype):
    """
    Validate sample_datasets type for a given column
    Args:
        df: input dataframe
        column: column to validate its sample_datasets type
        target_dtype: desired dtype

    Return:
        Boolean: True if the dtype of the given column is consistent with target dtype
    """

    data_type = dict(df.dtypes)[column]
    return str(data_type) == target_dtype


def validate_timestamp(df):
    """
    Validate id timestamps are sorted, compliant with ISO 8601 format and not duplicated
    Args:
        df: input dataframe

    Return:
        Boolean flag: True if valid timestamps
    """
    if not "timestamp" in df.columns:
        raise ValueError("timestamp column not found!")

    if is_null(df, "timestamp"):
        raise ValueError("Missing timestamp!")

    if is_duplicate(df, ["timestamp"]):
        raise ValueError("Duplicate timestamp!")

    def validate(ts, fmt="%Y-%m-%dT%H:%M:%SZ"):
        try:
            datetime.strptime(str(ts), fmt)
        except ValueError:
            return True
        return False

    validate_timestamp = F.udf(lambda x: validate(x))
    # check if format is iso 8601
    df = df.withColumn("isbad", validate_timestamp(F.col("timestamp")))

    if df.where(df.isbad == True).count() > 0:
        raise ValueError("timestamps not is ISO 8601 format")
    # check if timestamps are given sorted
    df = df.withColumn("idx1", F.monotonically_increasing_id())
    df = orderby_timestamp(df)
    df = df.withColumn("idx2", F.monotonically_increasing_id())
    df = df.withColumn(
        "not_sorted",
        F.when((F.col("idx1") != F.col("idx2")), True).otherwise(False),
    )
    if df.where(df.not_sorted == True).count() > 0:
        raise ValueError("timestamps not sorted!")


def valid_num_of_columns(df):
    return len(df.columns) - 1 <= MAX_NUM_COL


def valid_num_of_datapoints(df):
    return df.count() <= MAX_DATAPOINTS


def valid_header(df):
    if not "timestamp" in df.columns:
        return False
    for col in df.columns:
        if col.replace(" ", "") == "":
            return False
    return True


def is_sufficient_datapoints(df):
    return df.count() >= 6 * MAX_NUM_COL


def all_columns_null(df):
    for c in df.columns:
        if c == "timestamp":
            continue
        if df.filter(F.col(c).isNull() | F.isnan(c)).count() != df.count():
            return False
    return True


def validate_data(df):

    if not valid_header(df):
        raise ValueError("Invalid header")
    if not valid_num_of_datapoints(df):
        raise ValueError(f"Number of data points exceed {MAX_DATAPOINTS}")
    if not valid_num_of_columns(df):
        raise ValueError(f"Number of signals exceed {MAX_NUM_COL}")
    if all_columns_null(df):
        raise ValueError("At least one none Null column required")
    if not is_sufficient_datapoints(df):
        raise ValueError("Insufficient sample_datasets")
    for col in df.columns:
        if col == "timestamp":
            continue
        if not valid_dtype(df, col, "double"):
            raise TypeError(f"Data type of column {col} is not numeric")
    validate_timestamp(df)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    args = parser.parse_args()

    spark = create_spark_session("pySpark_data_validation")
    with open(args.input) as f:
        header = f.readline().split(",")
    if len(set(header)) != len(header):
        raise ValueError("Duplicate signal name!")

    input_data = spark.read.csv(args.input, sep=",", inferSchema=False, header=True)
    validate_data(input_data)


if __name__ == "__main__":
    main()
