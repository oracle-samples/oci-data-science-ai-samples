#!/bin/bash

echo "start-vllm.sh"

echo "select authentication method"
if [[ -z "${MODEL_DEPLOYMENT_OCID}" ]]; then
  auth_method=instance_principal
else
  auth_method=resource_principal
fi

echo "authentication method: ${auth_method}"

if [ -n "$BUCKET" ]; then
  echo "BUCKET variable are set: $BUCKET"
  /root/bin/oci os object sync --auth $auth_method --bucket-name $BUCKET --dest-dir /home/datascience/model/
  MODEL="/home/datascience/model/$MODEL"  
elif [ -n "$TOKEN_FILE" ]; then
  echo "Checking internet connection: "
  curl -s --connect-timeout 15 http://example.com > /dev/null && echo "Connected" || echo "Not connected"
  export HUGGING_FACE_HUB_TOKEN=$(cat $TOKEN_FILE)
  echo "The md5 of token is $(md5sum $TOKEN_FILE)"
  mkdir -p /home/datascience/.cache/huggingface
  cp $TOKEN_FILE /home/datascience/.cache/huggingface/token
  echo "Copied token file to /home/datascience/.cache/huggingface, $(md5sum /home/datascience/.cache/huggingface/token)"
  echo "Set HuggingFace cache folder..."
  export HUGGINGFACE_HUB_CACHE=/home/datascience/.cache
  echo "The size of partitions"
  echo $(df -h /home/datascience)
  df -h
  echo $(du -sh /home/datascience/*)
else
  echo "No bucket or authentication token is provided. Weights are assumed to be downloaded from OCI Model Catalog."
  MODEL="/opt/ds/model/deployed_model/$MODEL"
  echo $MODEL
fi

# Get the number of GPUs using nvidia-smi and assign it to a variable
NUM_GPUS=$(nvidia-smi --list-gpus | wc -l)
echo "Number of GPUs detected: $NUM_GPUS"

echo "Starting vllm engine..."
source activate vllm
echo "Running command: WEB_CONCURRENCY=1 python $VLLM_DIR/vllm-api-server.py --port $PORT --host 0.0.0.0 --log-config $VLLM_DIR/vllm-log-config.yaml --model $MODEL --tensor-parallel-size $NUM_GPUS"
WEB_CONCURRENCY=1 python $VLLM_DIR/vllm-api-server.py --port $PORT --host 0.0.0.0 --log-config $VLLM_DIR/vllm-log-config.yaml --model $MODEL --tensor-parallel-size $NUM_GPUS

echo "Exiting vLLM. Here is the disk utilization of /home/datascience - "
echo $(du -sh /home/datascience)
echo "server logs: "
ls -lah /home/datascience
cat /home/datascience/server.log
