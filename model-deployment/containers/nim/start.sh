#!/bin/bash 
if [ -z "$NGC_API_KEY_FILE" ] ; then
  echo "No NGC API key file is provided. Process will terminate."
  exit 1
else
  export NGC_API_KEY=$(cat $NGC_API_KEY_FILE)
  echo "Starting server..."
  /opt/nim/start-server.sh
  exit $LastExitCode
fi

