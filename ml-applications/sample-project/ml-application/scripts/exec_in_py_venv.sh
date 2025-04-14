#!/bin/bash
set -e

install_libs() {
  # update/install libs
  pip3 install -U -r "${script_dir}/requirements.txt"

  # update/install preview OCI SDK
  required_oci_sdk_version="$1"

  # As checking oci preview SDK is installed in correct version is quite long lasting operation we do following
  installed_version=$(pip freeze | grep 'oci==' | cut -d '=' -f3)
  if [ "$installed_version" == "$required_oci_sdk_version" ]; then
    echo "The required $required_oci_sdk_version version of the oci library is installed."
  else
    echo "The required version $required_oci_sdk_version of the oci library is not installed (installed version: $installed_version). Installing it ..."
    pip3 install --trusted-host=artifactory.oci.oraclecorp.com -i https://artifactory.oci.oraclecorp.com/api/pypi/global-dev-pypi/simple -U oci==$required_oci_sdk_version
  fi
}

# Check if a parameter was provided
if [ $# -lt 1 ]; then
    echo "Usage: $(filename $0) <python_script_to_execute> [argument1] [argument2] ..."
    exit 1
fi

echo "Setting up Python environment ..."

this_script=$(realpath "$0")
script_dir=$(dirname "$this_script")
python_script=$1
lib_version_hash_file="${script_dir}/lib_version.hash"
sdk_version_file="${script_dir}/oci_sdk_version.txt"
required_oci_sdk_version=$(cat $sdk_version_file)

shift # Remove the first argument from the list of arguments

#[[ -n "$VIRTUAL_ENV" ]] && deactivate #|| echo "No virtual environment is active."
python3 -m venv "$script_dir/.venv"
source "${script_dir}/.venv/bin/activate"

if [ ! -f $lib_version_hash_file ]; then
  echo "lib_version.hash not found, creating..."
  echo "" > $lib_version_hash_file
fi

hash_val=$(cat ${sdk_version_file} ${script_dir}/requirements.txt | sha256sum | awk '{print $1}')
old_hash=$(cat $lib_version_hash_file)

if [ "${hash_val}" != "${old_hash}" ]; then
  echo "Python libs must be updated ..."
  install_libs $required_oci_sdk_version
  echo "${hash_val}" > "$lib_version_hash_file"
else
  echo "Python libs up-to-date"
fi



echo "Executing Python script: $script_dir/$python_script $@"
echo "------------------------------------------------------"
python3 $script_dir/$python_script "$@"
deactivate
