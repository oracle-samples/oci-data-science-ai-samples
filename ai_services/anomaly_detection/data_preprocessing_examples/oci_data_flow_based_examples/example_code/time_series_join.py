# Copyright © 2021, Oracle and/or its affiliates.

import argparse
from pyspark.sql import SparkSession


class parse_kwargs(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        values = values[0].split(" ") if len(values) == 1 else values
        setattr(namespace, self.dest, values)


def timeseries_join(dfs):
    if len(dfs) < 2:
        return dfs
    for i in range(len(dfs)):
        if "timestamp" in dfs[i].columns:
            continue
        raise ValueError("timestamp not found!")

    all_columns = \
        [col for df in dfs for col in df.columns if col != "timestamp"]
    if len(set(all_columns)) != len(all_columns):
        raise ValueError("Columns are not distinct")

    df = dfs[0]
    for i in range(1, len(dfs)):
        df = df.join(dfs[i], ["timestamp"], "outer")
    return df


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        nargs="+",
        required=True,
        action=parse_kwargs)
    parser.add_argument("--output", required=True)
    parser.add_argument("--coalesce", required=False, action="store_true")

    args = parser.parse_args()
    spark = SparkSession.builder.appName("DataFlow").getOrCreate()
    dfs = [spark.read.csv(fname, header=True) for fname in args.input]
    df = timeseries_join(dfs)

    if args.coalesce:
        df.coalesce(1).write.csv(args.output, header=True)
    else:
        df.write.csv(args.output, header=True)
