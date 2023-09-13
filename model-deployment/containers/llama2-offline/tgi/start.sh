#!/bin/bash 
echo "Starting TGI..."
text-generation-launcher --json-output --hostname 0.0.0.0 --port $PORT --model-id $MODEL $PARAMS