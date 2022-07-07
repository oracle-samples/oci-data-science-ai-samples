#!/bin/bash
pip install wheel setuptools
python setup.py bdist_wheel
if [ ! -d "dtst" ]
then
    cd dist
    docker pull phx.ocir.io/oracle/dataflow/dependency-packager:latest
    docker run --rm -v $(pwd):/opt/dataflow --pull always -it phx.ocir.io/oracle/dataflow/dependency-packager:latest -p 3.6
else
    echo "Error: Directory dist does not exists. Please rerun the setup.py."
fi
