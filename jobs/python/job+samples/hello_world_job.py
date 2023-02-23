# get the job code path, works in JL Notebook! 
import time, sys
from pathlib import Path

print("Hello world!")
time.sleep(3)

# 
current_path = Path(sys.path[0])
print (f'current path: {current_path}')

print("Job Done.")