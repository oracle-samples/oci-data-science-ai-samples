echo "start-sdxl.sh"

echo "select authentication method"
if [[ -z "${MODEL_DEPLOYMENT_OCID}" ]]; then
  auth_method=instance_principal
else
  auth_method=resource_principal
fi

echo "authentication method: ${auth_method}"

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

# Get the number of GPUs using nvidia-smi and assign it to a variable
NUM_GPUS=$(nvidia-smi --list-gpus | wc -l)
echo "Number of GPUs detected: $NUM_GPUS"

echo "Starting SDXL engine..."
source activate sdxl
WEB_CONCURRENCY=1 python $SDXL_DIR/sdxl-api-server.py --port ${PORT} --host 0.0.0.0 --log-config $SDXL_DIR/sdxl-log-config.yaml

echo "Exiting SDXL. Here is the disk utilization of /home/datascience - "
echo $(du -sh /home/datascience)
echo "Server logs: "
ls -lah /opt/sdxl
cat /opt/sdxl/server.log
