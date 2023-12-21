#!/bin/bash
echo "tritonserver:model_repository_path" : $1;
echo "tritonserver:mode " : $2;
echo "tritonserver:http-port " : $3;


exec /opt/tritonserver/bin/tritonserver --model-repository=$1 --model-control-mode=$2 --http-port=$3 --allow-gpu-metrics=false