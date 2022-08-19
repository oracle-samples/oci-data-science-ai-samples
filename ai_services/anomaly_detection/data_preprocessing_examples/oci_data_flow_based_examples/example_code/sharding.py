from pyspark.sql import SparkSession
import argparse
import math


class ParseKwargs(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        values = values[0].split(" ") if len(values) == 1 else values
        if ":" not in values[0]:
            setattr(namespace, self.dest, values)
        else:
            setattr(namespace, self.dest, dict())
            for value in values:
                key, value = value.split(":")
                getattr(namespace, self.dest)[key] = value


def sharding(df, partition_size, output, idcols):
    """
    Vertical data sharding
    Args:
        df : input dataframe
        partition_size : max number of columns in the partitioned data
        output :  destination to store output
        coalesce : whether to combine partitions into a single CSV file
        idcols: identifiers of each record - in addition to timestamp

    Return:
        partitions of the original dataframe in CSV format
    """
    sharding_dict = dict()
    column_names = df.columns
    idcols = ["timestamp"] + idcols if idcols else ["timestamp"]
    for col in idcols:
        if col not in column_names:
            raise ValueError(f"{col} column not found!")
    for col in idcols:
        column_names.remove(col)

    k = len(idcols) - 1
    num_columns = len(column_names) - k
    partition_size -= k
    num_partitions = math.ceil(num_columns / partition_size)

    for i in range(num_partitions):
        partition_columns = column_names[
            i * partition_size:min(num_columns, (i + 1) * partition_size)
        ]
        for col in reversed(idcols):
            partition_columns.insert(0, col)

        df_partition = df.select(*partition_columns)
        output_name = output + "_part_" + str(i + 1)
        sharding_dict[output_name] = df_partition

    return sharding_dict


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument(
        "--idColumns",
        nargs="*",
        required=False,
        action=ParseKwargs)
    parser.add_argument("--columnNum", required=False, default="300")
    parser.add_argument("--coalesce", required=False, action="store_true")
    args = parser.parse_args()

    spark = SparkSession.builder.appName("PySpark_Sharding").getOrCreate()
    df_input = spark.read.load(
        args.input, format="csv", sep=",", inferSchema="true", header="true"
    )
    sharded_dfs = sharding(
        df_input,
        partition_size=int(args.columnNum),
        output=args.output,
        idcols=args.idColumns
    )

    for output_name, df_partition in sharded_dfs.items():
        if args.coalesce:
            df_partition.coalesce(1).write.csv(output_name, header=True)
        else:
            df_partition.write.csv(output_name, header=True)
