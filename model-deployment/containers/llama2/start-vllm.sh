#!/bin/bash

if [ -z "$TOKEN_FILE" ] ; then
  echo "No authentication token is provided. Weights are assumed to be downloaded from OCI Model Catalog."
else
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
  echo "Checking internet connection: "
  curl -sI -v https://www.wikipedia.org
  echo $(du -sh /home/datascience/*)
fi

echo "Starting vllm engine..."
source activate vllm
WEB_CONCURRENCY=1 python $INSTALL_DIR/vllm-api-server.py --port ${PORT} --host 0.0.0.0 --log-config $INSTALL_DIR/vllm-log-config.yaml --model ${MODEL} --tensor-parallel-size ${TENSOR_PARALLELISM} ${PARAMS}


echo "Exiting vLLM. Here is the disk utilization of /home/datascience - "
echo $(du -sh /home/datascience)
echo "server logs: "
ls -lah /home/datascience
cat /home/datascience/server.log