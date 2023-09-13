#!/bin/bash

#This file allows you to install a custom conda environment
#If you want to install a service conda provided by OCI DS, modify line 22 to odsc conda install -s "$ENV_NAME"

# enable conda commands
source /etc/profile.d/enableconda.sh

# Replace this with name of the conda environment to create or activate
ENV_NAME="{ODSC_CONDA_PACK_SLUG}"

# Path to the conda environment folder
ENV_FOLDER="$HOME/conda"

# Check if the conda environment exists
if [ -d "$ENV_FOLDER/$ENV_NAME" ]
then
    echo "Conda environment '$ENV_NAME' found."
else
    echo "Conda environment '$ENV_NAME' not found, installing..."
    odsc conda install -s "$ENV_NAME" -o
fi

# Activate the conda environment
conda activate "$ENV_FOLDER"/"$ENV_NAME"

echo "Conda environment '$ENV_NAME' is now activated."
