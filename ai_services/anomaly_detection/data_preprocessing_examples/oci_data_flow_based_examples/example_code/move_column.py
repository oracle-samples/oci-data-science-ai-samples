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


def move_column(input_data, column_name, position):
    """
    Move a given column to a given position

    :param input_data: Input data file as dataframe
    :param column_name: Column which needs to be moved
    :param position: Position number to which the column_name needs to be moved
    :return: Dataframe with column_name moved to position number
    """

    columns = input_data.columns
    if position > len(columns) or position < 0:
        raise ValueError('position value should be between'
                         ' 0 and number of columns in the input data')
    columns.remove(column_name)
    columns.insert(position, column_name)
    df_moved_byposition = input_data.select(columns)
    return df_moved_byposition


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--column_name", required=True)
    parser.add_argument("--position", type=int, required=False, default=-1)
    parser.add_argument("--coalesce", required=False, action="store_true")
    args = parser.parse_args()

    spark = create_spark_session("DataFlow")
    input_data = spark.read.csv(args.input, sep=",",
                                inferSchema=True, header=True)
    input_data_columnmoved = move_column(input_data,
                                         args.column_name, args.position)
    if args.coalesce:
        input_data_columnmoved.coalesce(1).write.csv(args.output, header=True)
    else:
        input_data_columnmoved.write.csv(args.output, header=True)
