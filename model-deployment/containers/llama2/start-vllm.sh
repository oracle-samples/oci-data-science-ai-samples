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

#echo $(du -sh /home/datascience/*)
echo "The size of partitions"
#echo $(df -h /home/datascience)
df -h
#echo $(du -sh /home/datascience)

echo "Checking internet connection: "

printenv

curl -sI -v https://www.wikipedia.org

echo $(du -sh /home/datascience/*)

# echo "starting nginx server and vllm"
# nginx -p $PWD && \
# source activate vllm && \
# WEB_CONCURRENCY=1 python $VLLM_DIR/vllm-api-server.py --port 80 --host 0.0.0.0 --log-config $VLLM_DIR/vllm-log-config.yaml $PARAMS

echo "Check if Nginx is running"
if pgrep -x "nginx" > /dev/null
then
    echo "Stopping Nginx..."
    nginx -s stop
fi

# Start Nginx and the VLLM API server
echo "Starting Nginx and VLLM API server..."
nginx -p $PWD && \
source activate vllm && \
WEB_CONCURRENCY=1 python $VLLM_DIR/vllm-api-server.py --port 80 --host 0.0.0.0 --log-config $VLLM_DIR/vllm-log-config.yaml $PARAMS


echo "Exiting vLLM. Here is the disk utilization of /home/datascience - "
echo $(du -sh /home/datascience)
echo "server logs: "
ls -lah /home/datascience
cat /home/datascience/server.log
