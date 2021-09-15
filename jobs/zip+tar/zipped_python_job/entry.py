import os
import sys
import datetime
from utils.log import Logging

JOB_RUN_OCID_KEY = "JOB_RUN_OCID"
LOG_OBJECT_OCID_KEY = "LOG_OBJECT_OCID"

if __name__ == "__main__":
    try:

        job = Logging()

        job.log(
            [
                "Start logging for job run: {}".format(
                    os.environ.get(JOB_RUN_OCID_KEY, "LOCAL")
                ),
                "Current timestamp in UTC: {}".format(str(datetime.datetime.utcnow())),
            ]
        )

        job.log(["Job Done."])

    except Exception as e:
        print(e)
        raise e
