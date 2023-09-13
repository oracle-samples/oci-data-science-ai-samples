import os, sys
from datetime import datetime

# Max 255 error code
SUCCESS = 251

# Set custom code, NOTICE the code has to be a Number!
ERROR_CODE = int(os.environ.get("CODE", SUCCESS))

print(f'Job Run {datetime.now().strftime("%m-%d-%Y-%H:%M:%S")}')

if ERROR_CODE != SUCCESS:
    print(f"Job should exit with code:  ({ERROR_CODE})")
    sys.exit(ERROR_CODE)
else:
    print("Job Done.")
