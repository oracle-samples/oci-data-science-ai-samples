#!/bin/bash 
if [ -z "$NGC_API_KEY_FILE" ] ; then
  echo "No NGC API key file is provided. Process will terminate."
  exit 1
else
  export NGC_API_KEY=$(cat $NGC_API_KEY_FILE)
  echo "Starting server..."
  # At present, there does not seem to exist any NIM configuration to successfully override max model length, so need to manually configure vLLM command
  WEB_CONCURRENCY=1 python3 -m vllm_nvext.entrypoints.openai.api_server --max-model-len 2048 --enforce-eager --tensor-parallel-size 2
  exit $?
fi

