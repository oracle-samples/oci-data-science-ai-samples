#!/bin/bash 

export HUGGING_FACE_HUB_TOKEN=$(cat $TOKEN_FILE)
echo "The md5 of token is $(md5sum $TOKEN_FILE)"
mkdir -p /home/datascience/.cache/huggingface
cp $TOKEN_FILE /home/datascience/.cache/huggingface/token
echo "Copied token file to /home/datascience/.cache/huggingface, $(md5sum /home/datascience/.cache/huggingface/token)"

echo "Set HuggingFace cache folder..."
export HUGGINGFACE_HUB_CACHE=/home/datascience/.cache

echo "Set new tmp/ folder"
mkdir -p /home/datascience/tmp
export TMPDIR=/home/datascience/tmp

echo "Checking internet connection: "
curl -sI -v https://www.wikipedia.org

# echo $(du -sh /home/datascience/*)

echo "starting nginx server and vllm"
nginx -p $PWD && WEB_CONCURRENCY=1 python /etc/vllm-api-server.py --port 80 --host 0.0.0.0 --log-config /etc/vllm-log-config.yaml $PARAMS

echo "Exiting vLLM. Here is the disk utilization of /home/datascience - "
echo $(du -sh /home/datascience)
# 
echo "server logs ..."
ls -lah /home/datascience
cat /home/datascience/server.log 
