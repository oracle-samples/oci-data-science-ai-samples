TENANCY:=${TENANCY_NAME}
CONTAINER_REGISTRY:=${REGION_KEY}.ocir.io

TGI_INFERENCE_IMAGE:=${CONTAINER_REGISTRY}/${TENANCY}/text-generation-interface-odsc:0.9.3
TGI_CONTAINER_NAME:=tgi-odsc

VLLM_INFERENCE_IMAGE:=${CONTAINER_REGISTRY}/${TENANCY}/vllm-odsc:0.2.0
VLLM_CONTAINER_NAME:=vllm-odsc

MODEL_DIR:=${PWD}/hfdata
TARGET_DIR:=/home/datascience
HF_DIR=/home/datascience/.cache

token:=${PWD}/token
target_token:=/opt/ds/model/deployed_model/token
model:=meta-llama/Llama-2-7b-chat-hf
port:=8080
params:="--max-batch-prefill-tokens 1024"
local_model:=/opt/ds/model/deployed_model
tensor_parallelism:=1

check-env:
	@if [[ -z "$${TENANCY_NAME}" ]]; then \
		echo "TENANCY_NAME is not set or is empty"; \
		exit 1; \
	fi
	@if [[ -z "$${REGION_KEY}" ]]; then \
		echo "REGION_KEY is not set or is empty"; \
		exit 1; \
	fi
	@echo "Both TENANCY_NAME and REGION_KEY are set and have values."
build.tgi:
	cd tgi/ && docker build --network host -t ${TGI_INFERENCE_IMAGE} -f Dockerfile.tgi .
build.vllm: check-env
	cd vllm/ && docker build --network host -t ${VLLM_INFERENCE_IMAGE} -f Dockerfile.vllm .
run.tgi.hf:
	docker run --rm -it --gpus all --shm-size 1g -p ${port}:${port} -e PORT=${port} -e TOKEN_FILE=${target_token} -e PARAMS=${params} -e MODEL=${model} -v ${MODEL_DIR}:${TARGET_DIR} -v ${token}:${target_token} --name ${TGI_CONTAINER_NAME} ${TGI_INFERENCE_IMAGE}
run.tgi.oci:
	docker run --rm -it --gpus all --shm-size 1g -p ${port}:${port} -e PORT=${port} -e PARAMS=${params} -e MODEL=${local_model} -v ${MODEL_DIR}:${TARGET_DIR} --name ${TGI_CONTAINER_NAME} ${TGI_INFERENCE_IMAGE}
run.vllm.hf:
	docker run --rm -it --gpus all --shm-size 1g -p ${port}:${port} -e PORT=${port} -e UVICORN_NO_USE_COLORS=1 -e TOKEN_FILE=${target_token} -e MODEL=${model} -e TENSOR_PARALLELISM=${tensor_parallelism} -e HUGGINGFACE_HUB_CACHE=${HF_DIR} -v ${MODEL_DIR}:${TARGET_DIR} -v ${token}:${target_token} --name ${VLLM_CONTAINER_NAME} ${VLLM_INFERENCE_IMAGE}
run.vllm.oci:
	docker run --rm -d --gpus all --shm-size 1g -p ${port}:${port} -e PORT=${port} -e UVICORN_NO_USE_COLORS=1 -e MODEL=${local_model} -e TENSOR_PARALLELISM=${tensor_parallelism} -v ${MODEL_DIR}:${TARGET_DIR} --name ${VLLM_CONTAINER_NAME} ${VLLM_INFERENCE_IMAGE}
shell.tgi:
	docker run --rm -it --shm-size=1g --net host -p ${port}:${port} -e TOKEN_FILE=${target_token} -e PARAMS="--model-id ${model}" --entrypoint bash -v ${MODEL_DIR}:${TARGET_DIR} -v ${token}:${target_token} --name ${TGI_CONTAINER_NAME} ${TGI_INFERENCE_IMAGE} 
shell.vllm:
	docker run --rm -it --shm-size=15g --net host -p ${port}:${port} -e TOKEN_FILE=${target_token} -e PARAMS="--model ${model}" -e HUGGINGFACE_HUB_CACHE=${HF_DIR} --entrypoint bash -v ${MODEL_DIR}:${TARGET_DIR} -v ${token}:${target_token} --name ${VLLM_CONTAINER_NAME} ${VLLM_INFERENCE_IMAGE} 
stop.tgi:
	docker stop ${TGI_CONTAINER_NAME}
stop.vllm:
	docker stop ${VLLM_CONTAINER_NAME}
push.tgi:
	docker push ${TGI_INFERENCE_IMAGE}
push.vllm:
	docker push ${VLLM_INFERENCE_IMAGE}
