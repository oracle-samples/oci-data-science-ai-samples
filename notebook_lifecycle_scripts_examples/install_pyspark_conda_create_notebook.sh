#!/bin/bash

#This script allows you to install pyspark conda environment to work with data flow in data science notebook session. It creates a ipynb  file that imports ads and loads the SparkMagic extension

# enable conda commands
source /etc/profile.d/enableconda.sh

ENV_NAME=pyspark32_p38_cpu_v3

# Path to the conda environment folder
ENV_FOLDER="$HOME/conda"

# Check if the conda environment exists
if [ -d "$ENV_FOLDER/$ENV_NAME" ]
then
    echo "Conda environment '$ENV_NAME' found."

else
    echo "Conda environment '$ENV_NAME' not found, installing..."
    odsc conda install -s "$ENV_NAME"
fi

# Activate the conda environment
conda activate "$ENV_FOLDER"/"$ENV_NAME"

echo "Conda environment '$ENV_NAME' is now activated."


cat << EOF > pyscript.py
import os
os.system("source activate conda/pyspark32_p38_cpu_v3")
import subprocess

import nbformat as nbf
from nbformat.v4 import new_code_cell, new_notebook, new_markdown_cell

cells = []
cells.append(new_markdown_cell(
    source='import ADS and load the SparkMagic extension',
))


cells.append(new_code_cell(
    source='import ads\nads.set_auth("resource_principal")\n%load_ext dataflow.magics',
    execution_count=1,
))


nb0 = new_notebook(cells=cells,
    metadata={
        'language': 'python',
    }
)

import codecs
f = codecs.open('dataflow_notebook.ipynb', encoding='utf-8', mode='w')
nbf.write(nb0, f, 4)
f.close()
EOF

chmod 755 pyscript.py
python pyscript.py
