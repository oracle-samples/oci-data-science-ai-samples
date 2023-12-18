# Initial setup to create the version file if it doesn't exist
init:
	@if [ ! -f version.txt ]; then \
		echo 0 > version.txt; \
	fi

increment_version:
	@echo "Incrementing version..."
	@echo $$(($$(cat version.txt) + 1)) > version.txt

TENANCY:=${TENANCY_NAME}
CONTAINER_REGISTRY:=${REGION_KEY}.ocir.io

TGI_INFERENCE_IMAGE:=${CONTAINER_REGISTRY}/${TENANCY}/text-generation-interface-odsc:0.9.3-v
TGI_CONTAINER_NAME:=tgi-odsc

VLLM_INFERENCE_IMAGE:=${CONTAINER_REGISTRY}/${TENANCY}/vllm-odsc:0.2.2-v
VLLM_CONTAINER_NAME:=vllm-odsc

SDXL_INFERENCE_IMAGE:=${CONTAINER_REGISTRY}/${TENANCY}/sdxl:1.0.

MODEL_DIR:=${PWD}/hfdata
TARGET_DIR:=/home/datascience
HF_DIR=/home/datascience/.cache

token:=${PWD}/token
target_token:=/opt/ds/model/deployed_model/token
model:=meta-llama/Llama-2-13b-chat-hf
port:=8080
params:="--max-batch-prefill-tokens 1024"
local_model:=/opt/ds/model/deployed_model
tensor_parallelism:=1

# Detect the architecture of the current machine
ARCH := $(shell uname -m)

# Define the Docker build command based on the architecture
ifeq ($(ARCH),arm64)
    DOCKER_BUILD_CMD := docker buildx build --platform linux/amd64
else
    DOCKER_BUILD_CMD := docker build
endif

check-env:
	@if [ -z "$${TENANCY_NAME}" ] || [ -z "$${REGION_KEY}" ]; then \
		echo "TENANCY_NAME or REGION_KEY is not set or is empty"; \
		exit 1; \
	fi

build.tgi: check-env init increment_version
	$(DOCKER_BUILD_CMD) --network host \
	-t ${TGI_INFERENCE_IMAGE}$(shell cat version.txt) \
	-f Dockerfile.tgi .

build.vllm: check-env init increment_version
	$(DOCKER_BUILD_CMD) --network host \
	-t ${VLLM_INFERENCE_IMAGE}$(shell cat version.txt) \
	-f Dockerfile.vllm .

build.sdxl: check-env init increment_version
	$(DOCKER_BUILD_CMD) --network host \
	-t ${SDXL_INFERENCE_IMAGE}$(shell cat version.txt) \
	-f Dockerfile.sdxl .

run.tgi.hf: check-env
	docker run --rm -it --gpus all --shm-size 1g \
	-p ${port}:${port} \
	-e PORT=${port} \
	-e TOKEN_FILE=${target_token} \
	-e PARAMS=${params} \
	-e MODEL=${model} \
	-v ${MODEL_DIR}:${TARGET_DIR} \
	-v ${token}:${target_token} \
	--name ${TGI_CONTAINER_NAME} ${TGI_INFERENCE_IMAGE}

run.tgi.oci: check-env
	docker run --rm -it --gpus all --shm-size 1g \
	-p ${port}:${port} \
	-e PORT=${port} \
	-e PARAMS=${params} \
	-e MODEL=${local_model} \
	-v ${MODEL_DIR}:${TARGET_DIR} \
	--name ${TGI_CONTAINER_NAME} ${TGI_INFERENCE_IMAGE}

run.vllm.hf: check-env
	docker run --rm -it --gpus all --shm-size 1g \
	-p ${port}:${port} \
	-e PORT=${port} \
	-e UVICORN_NO_USE_COLORS=1 \
	-e TOKEN_FILE=${target_token} \
	-e MODEL=${model} \
	-e TENSOR_PARALLELISM=${tensor_parallelism} \
	-e HUGGINGFACE_HUB_CACHE=${HF_DIR} \
	-v ${MODEL_DIR}:${TARGET_DIR} \
	-v ${token}:${target_token} \
	--name ${VLLM_CONTAINER_NAME} ${VLLM_INFERENCE_IMAGE}

run.vllm.oci: check-env
	docker run --rm -d --gpus all --shm-size 1g \
	-p ${port}:${port} \
	-e PORT=${port} \
	-e UVICORN_NO_USE_COLORS=1 \
	-e MODEL=${local_model} \
	-e TENSOR_PARALLELISM=${tensor_parallelism} \
	-v ${MODEL_DIR}:${TARGET_DIR} \
	--name ${VLLM_CONTAINER_NAME} ${VLLM_INFERENCE_IMAGE}

stop.tgi: check-env
	docker stop ${TGI_CONTAINER_NAME}$(shell cat version.txt)

stop.vllm: check-env
	docker stop ${VLLM_CONTAINER_NAME}$(shell cat version.txt)

push.tgi: check-env
	docker push ${TGI_INFERENCE_IMAGE}$(shell cat version.txt)

push.vllm: check-env
	docker push ${VLLM_INFERENCE_IMAGE}$(shell cat version.txt)

push.sxl: check-env
	docker push ${SDXL_INFERENCE_IMAGE}$(shell cat version.txt)

app:
	MODEL=${model} gradio app.py
