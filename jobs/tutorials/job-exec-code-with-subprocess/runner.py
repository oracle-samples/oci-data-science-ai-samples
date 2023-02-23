import os
import sys
import subprocess
import importlib.util
import argparse
from pathlib import Path
from subprocess import PIPE, Popen
from datetime import datetime

print(f'Job code runner {datetime.now().strftime("%m-%d-%Y-%H:%M:%S")} ...')

# set -f as command line argument on the job/job run to change which file should be ran
parser = argparse.ArgumentParser()
parser.add_argument("-f", "--file", required=False, default="get-cpu-info.py")
parser.add_argument("positional_args", nargs="*")
args = parser.parse_args()

print(f"File to execute set to: {args.file}")


# get current code path
current_path = Path(sys.path[0])
print (f'current path: {current_path}')

def install(package):
    # subprocess.run(['pip', 'install', package])
    # ... or
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# verify if the library exist, if not install it
spec = importlib.util.find_spec("cpuinfo")
if spec is None:
    print("package py-cpuinfo does not exist, installing...")
    install("py-cpuinfo")
else:
    print("py-cpuinfo exist")

# which file to run
FILE_NAME = f'{current_path}/{args.file}'
print(f"Full path: {FILE_NAME}")

# Pass the command line arguments to the code, if any
# Notice environment variables set on the job/job run will be also avaiable in the subprocess
cmd = [sys.executable, FILE_NAME]
print(f"Positional arguments: {args.positional_args}")

# args = sys.argv[1:]
# _args = args.positional_args[1:]
if args.positional_args:
    cmd += args.positional_args

# Run the python script
print('\n')
print(f"Running command: {cmd}")
process = subprocess.Popen(cmd, stdout=subprocess.PIPE)

# Steam the outputs
while True:
    output = process.stdout.readline()
    if process.poll() is not None and output == b"":
        break
    if output:
        print(output.decode().strip())
