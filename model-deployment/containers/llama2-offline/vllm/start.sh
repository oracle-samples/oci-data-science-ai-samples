#!/bin/bash 

echo "Starting vllm engine..."
WEB_CONCURRENCY=1 python api-server.py --port ${PORT} --host 0.0.0.0 --log-config /etc/log-config.yaml --model ${MODEL} --tensor-parallel-size ${TENSOR_PARALLELISM}
 
