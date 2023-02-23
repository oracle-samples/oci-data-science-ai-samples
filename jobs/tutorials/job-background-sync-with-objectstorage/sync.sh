#!/bin/bash

echo "Sync Settings..."
echo $SYNC_DIR
echo $BUCKET
echo $OB_PREFIX
echo $JOB_OCID

# Set the error message
ERROR_MSG="An error occurred while syncing, it was not able to run the OCI CLI probably because it was not installed yet!"

# Define a function to handle errors
handle_error() {
  echo $ERROR_MSG
  exit 1
}

# Set the trap to execute the error handling function when an error occurs
trap 'handle_error' ERR

# Re-Run Duration
sleep_duration=10

# if [ "$JOB_OCID" = 'Undefined' ]; then
if [[ -z "${JOB_OCID}" ]]; then
  auth_method=api_key
  JOB_OCID="Undefined"
else
  auth_method=resource_principal
fi

echo "Auth Method: $auth_method"

# Check if the directory exists, try to create it if it doesn't
if [[ -d "$SYNC_DIR" && -n "$(ls -A "$SYNC_DIR")" ]]; then
  echo "Sync Directory: $SYNC_DIR"
else
  echo "Creating sync directory: $SYNC_DIR"
  if mkdir -p "$SYNC_DIR"; then
    echo "Sync directory created"
  else
    echo "Error: Unable to create sync directory" >&2
    exit 61
  fi
fi

# regulary check, maybe the folder to sync is removed later
while true; do
  if [[ -d $SYNC_DIR && -n "$(ls -A $SYNC_DIR)" ]]; then
    echo "Directory and data present, syncing..."
    oci os object sync --auth $auth_method --bucket-name $BUCKET --prefix $OB_PREFIX/$JOB_OCID/ --src-dir $SYNC_DIR
    # an error can happen if OCI CLI is not installed!
    if [ $? -ne 0 ]; then
      echo $ERROR_MSG
      exit 1
    fi    
  else
    echo "sync not running. sleeping*!"
  fi
  sleep $sleep_duration
done
