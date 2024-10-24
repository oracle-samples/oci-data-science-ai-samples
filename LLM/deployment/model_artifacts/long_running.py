"""This module contains a invoke() function that runs for more than 1 minute.

To invoke this with model deployment, make sure you specify the "async" parameter
in the payload to save the results into OCI object storage.
"""

import time


def invoke(inputs):
    f_time = time.time()
    time.sleep(90)
    t_time = time.time()
    return {
        "message": f"This is an example app running for {str(t_time - f_time)} seconds."
    }
