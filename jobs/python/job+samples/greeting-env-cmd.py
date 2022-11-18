from datetime import datetime
import os
import argparse

# Set NAME as environment variable on the job
NAME = os.environ.get("NAME", "UNDEFINED")

# set -g as command line argument on the job
parser = argparse.ArgumentParser()
parser.add_argument("-g", "--greeting", required=False, default="Hello")
args = parser.parse_args()


print(f'Job Run {datetime.now().strftime("%m-%d-%Y-%H:%M:%S")}')
print(f"{args.greeting}, your environment variable has value of ({NAME})")
print("Job Done.")
