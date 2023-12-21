#!/bin/bash 
if [ -z "$TOKEN_FILE" ] ; then
  echo "No authentication token is provided. Weights are assumed to be downloaded from OCI Model Catalog."
else
  echo "Checking internet connection: "
  curl -s --connect-timeout 15 http://example.com > /dev/null && echo "Connected" || echo "Not connected"
  export HUGGING_FACE_HUB_TOKEN=$(cat $TOKEN_FILE)
  echo "Downloading weights:"
  text-generation-server download-weights $MODEL
  echo "Download weights complete"
  echo $(du -sh /home/datascience/*)
fi

echo "Starting TGI..."
text-generation-launcher --json-output --hostname 0.0.0.0 --port $PORT --model-id $MODEL $PARAMS

echo "Exiting TGI. Here is the disk utilization of /home/datascience - "
echo $(du -sh /home/datascience)
exit $LastExitCode