#!/bin/bash
 
# This script sets up a pip configuration file for a specific repository.
 
# Set the URL of the repository to be used as the package index.
PYPI_URL=<Your repository URL here>
 
# Set this variable to true to disable the default PyPI index.
ENABLE_PYPI=true
 
# Set this variable to true to include the trusted host option in pip configuration.
ADD_TRUST=true
 
# If ENABLE_PYPI is true, set extra-index-url to PYPI_URL, otherwise skip it.
if [ "$ENABLE_PYPI" == "true" ]; then
  extra="extra-"
  index_url="index-url = ${PYPI_URL}"
else
  extra=""
  index_url=""
fi
 
# If ADD_TRUST is true, include trusted-host in pip configuration, otherwise skip it.
if [ "$ADD_TRUST" == "true" ]; then
  pypi_host=$(sed 's%^[^/]*//\([^/:]*\)[:/].*$%\1%' <<< "${PYPI_URL}")
  trusted_host="trusted-host = ${pypi_host}"
else
  trusted_host=""
fi
 
# Create the .pip directory in the home directory of the current user.
# If the directory already exists, this command will not overwrite it.
mkdir -p ~/.pip
 
# Write the pip configuration to the file ~/.pip/pip.conf.
cat > ~/.pip/pip.conf <<END
[global]
${extra}${index_url}
${trusted_host}
END
 
# Set the ownership of the .pip directory and its contents to the current user.
chown -R $(id -u):$(id -g) ~/.pip