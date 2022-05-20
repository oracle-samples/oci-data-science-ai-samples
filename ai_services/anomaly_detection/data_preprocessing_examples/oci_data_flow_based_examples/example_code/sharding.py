from pyspark.sql import SparkSession
import argparse
import math

def sharding(df, partition_size, output, coalesce):
    column_names = df.columns
    if 'timestamp' not in column_names:
        raise ValueError("timestamp column not found!")

    column_names.remove('timestamp')
    num_columns = len(column_names)
    num_partitions = math.ceil(num_columns / partition_size)

    for i in range(num_partitions):
        partition_columns = column_names[i * partition_size : min(num_columns, (i + 1) * partition_size)]
        partition_columns.insert(0, 'timestamp')
        df_partition = df.select(*partition_columns)
        output_name = output + "_part_" + str(i + 1)
        if coalesce:
            df_partition.coalesce(1).write.csv(output_name, header=True)
        else:
            df_partition.write.csv(output_name, header=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--columnNum", required=False, default='300')
    parser.add_argument("--coalesce", required=False, action="store_true")
    args = parser.parse_args()

    spark = SparkSession.builder.appName("PySpark_Sharding").getOrCreate()
    df_input = spark.read.load(
        args.input, format="csv", sep=",", inferSchema="true", header="true"
    )
    sharding(df_input, partition_size=int(args.columnNum), output=args.output, coalesce=args.coalesce)


if __name__ == "__main__":
    main()
