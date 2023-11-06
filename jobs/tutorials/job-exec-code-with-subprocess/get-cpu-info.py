# get the job code path, works in JL Notebook! 
import time, sys
from pathlib import Path
from cpuinfo import get_cpu_info

print("Getting CPU info...")

for key, value in get_cpu_info().items():
    print("{0}: {1}".format(key, value))


print("Job Done.")