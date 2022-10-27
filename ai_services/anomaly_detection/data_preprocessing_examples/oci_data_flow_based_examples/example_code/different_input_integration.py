from pyspark.sql import SparkSession
import argparse


def main(args):
    spark = SparkSession.builder.appName("DataFlow").getOrCreate()
    df1 = spark.read.csv(args.oos_input, header=True)

    if args.adw_adb_id:
        df2 = get_data_from_adw(args, spark)
        df1 = df1.unionByName(df2)

    if args.atp_adb_id:
        df3 = get_data_from_atp(args, spark)
        df1 = df1.unionByName(df3)

    df1 = df1.orderBy("timestamp")
    
    if args.coalesce:
        df1.coalesce(1).write.csv(args.output, header=True)
    else:
        df1.write.csv(args.output, header=True)


def get_data_from_adw(args, spark):
    return spark.read.format("oracle") \
        .option("adbId", args.adw_adb_id) \
        .option("dbtable", args.adw_dbtable) \
        .option("user", args.adw_username) \
        .option("password", args.adw_password) \
        .load()


def get_data_from_atp(args, spark):
    return spark.read.format("oracle") \
        .option("adbId", args.atp_adb_id) \
        .option("dbtable", args.atp_dbtable) \
        .option("user", args.atp_username) \
        .option("password", args.atp_password) \
        .load()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    # For this example, ObjectStore is a required input where as we're giving the flexibility to opt in/out of ATP/ADW.
    # The same can be altered based on the required flag mentioned below.

    parser.add_argument("--oos_input", required=True)
    parser.add_argument("--adw_adb_id", required=False)
    parser.add_argument("--adw_dbtable", required=False)
    parser.add_argument("--adw_username", required=False)
    parser.add_argument("--adw_password", required=False)
    parser.add_argument("--atp_adb_id", required=False)
    parser.add_argument("--atp_dbtable", required=False)
    parser.add_argument("--atp_username", required=False)
    parser.add_argument("--atp_password", required=False)
    parser.add_argument("--output", required=True)
    parser.add_argument("--coalesce",  required=False, action="store_true")

    args = parser.parse_args()
    main(args)
