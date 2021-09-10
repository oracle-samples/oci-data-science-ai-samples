#!/usr/bin/env/python

import os

# This test artifact is specifically to test conda pack. CONDA_PREFIX is full path of where activated conda pack is.

print("Executing job artifact")
print(os.getenv("CONDA_PREFIX"))
print(os.getenv("CONDA_ENV_SLUG"))
print(os.getenv("JOB_RUN_ENTRYPOINT"))
print(os.getenv("KEY1"))
print(os.getenv("KEY2"))
print(os.getenv("spec"))
