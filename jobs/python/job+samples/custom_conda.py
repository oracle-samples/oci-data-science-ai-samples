# Exec against conda that has sklearn and schedule packages installed!
# Demonstrates:
# - how to read the job enviornment variables
# - read the conda specific environment variables

import time
import sys
import os
import sklearn
import schedule


def get_by_key(key, default="LOCAL"):
    return os.environ.get(key, default)


print("Custom conda test!")


def job():
    print("Hello, Logs")
    time.sleep(5)


conda_type = get_by_key("CONDA_ENV_TYPE", "NONE")
conda_region = get_by_key("CONDA_ENV_REGION", "NONE")
conda_object_name = get_by_key("CONDA_ENV_OBJECT_NAME", "NONE")
conda_namespace = get_by_key("CONDA_ENV_NAMESPACE", "NONE")
conda_bucket = get_by_key("CONDA_ENV_BUCKET", "NONE")


print(f"CONDA_ENV_TYPE: {conda_type}")
print(f"CONDA_ENV_REGION: {conda_region}")
print(f"CONDA_ENV_OBJECT_NAME: {conda_object_name}")
print(f"CONDA_ENV_NAMESPACE: {conda_namespace}")
print(f"CONDA_ENV_BUCKET: {conda_bucket}")

print("The scikit-learn version is {}.".format(sklearn.__version__))

schedule.every().second.do(job)
schedule.run_all()

print("Job Done.")
