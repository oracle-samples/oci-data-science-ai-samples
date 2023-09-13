import os
import argparse

print("Starting hello.py")

# Set NAME as environment variable on the job
NAME = os.environ.get("NAME", "Job")

# set -g as command line argument on the job
parser = argparse.ArgumentParser(allow_abbrev=False)
parser.add_argument("-g", "--greeting", required=False, default="Hello")
args, unknown = parser.parse_known_args()

# to debug
# print(f'args: {args}')
# print(f'unknown: {unknown}')

print(f"{args.greeting} ({NAME})")
print("Job Done.")
