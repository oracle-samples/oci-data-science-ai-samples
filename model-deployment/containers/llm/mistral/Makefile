TENANCY:=${TENANCY_NAME}
CONTAINER_REGISTRY:=${REGION_KEY}.ocir.io

TGI_INFERENCE_IMAGE:=${CONTAINER_REGISTRY}/${TENANCY}/text-generation-interface-odsc:0.9.3
TGI_CONTAINER_NAME:=tgi-odsc

VLLM_INFERENCE_IMAGE:=${CONTAINER_REGISTRY}/${TENANCY}/vllm-odsc:0.1.4
VLLM_CONTAINER_NAME:=vllm-odsc

MODEL_DIR:=${PWD}/hfdata
TARGET_DIR:=/home/datascience
HF_DIR=/home/datascience/.cache

token:=${PWD}/token
target_token:=/opt/ds/model/deployed_model/token
model:=mistralai/Mistral-7B-Instruct-v0.1
port:=8080
params:="--max-batch-prefill-tokens 1024"
local_model:=/opt/ds/model/deployed_model
tensor_parallelism:=1

build.app:
	docker build --network host -t ${GRADIO_IMAGE} -f Dockerfile.gradio .
app:
	MODEL=${model} gradio app.py