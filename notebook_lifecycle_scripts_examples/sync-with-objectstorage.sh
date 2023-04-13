#!/bin/bash
 
echo "Sync to object storage..."
echo $NB_SYNC_DIR
echo $BUCKET
echo $BUCKET_PREFIX
echo $NB_SESSION_OCID
 
if [[ -z "${NB_SESSION_OCID}" ]]; then
  auth_method=api_key
else
  auth_method=resource_principal
 
oci os object sync --auth $auth_method --bucket-name $BUCKET --prefix $BUCKET_PREFIX --src-dir $NB_SYNC_DIR