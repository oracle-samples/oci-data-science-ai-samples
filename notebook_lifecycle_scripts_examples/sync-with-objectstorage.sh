#!/bin/bash

echo "Sync to object storage..."
echo $NB_SESSION_OCID
NB_SYNC_DIR="<nb_directory_to_sync>"
BUCKET="<object_storage_bucket>"
BUCKET_PREFIX="<object_storage_bucket_prefix>"

if [[ -z "${NB_SESSION_OCID}" ]]; then
  auth_method=api_key
else
  auth_method=resource_principal
fi

oci os object sync --auth $auth_method --bucket-name $BUCKET --prefix $BUCKET_PREFIX --src-dir $NB_SYNC_DIR
