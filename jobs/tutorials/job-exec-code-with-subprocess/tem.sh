#!/bin/sh
set- e
BASEDIR=$(dirname "$0")

# install the required python library
python -m pip install py-cpuinfo

# run the code
python $BASEDIR/get-cpu-info.py