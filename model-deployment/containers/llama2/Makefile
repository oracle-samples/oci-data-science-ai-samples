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

TGI_INFERENCE_IMAGE:=${CONTAINER_REGISTRY}/${TENANCY}/text-generation-interface:0.9.3-v
VLLM_INFERENCE_IMAGE:=${CONTAINER_REGISTRY}/${TENANCY}/vllm:0.2.6-v

# MODEL_DIR:=${PWD}/hfdata
MODEL_DIR:=${PWD}
TARGET_DIR:=/home/datascience
HF_DIR=/home/datascience/.cache

TOKEN:=${PWD}/token
TARGET_TOKEN:=/opt/ds/model/deployed_model/token
MODEL:=meta-llama/Llama-2-7b-chat-hf
PORT:=8080
PARAMS:="--max-batch-prefill-tokens 1024"
LOCAL_MODEL:=/opt/ds/model/deployed_model
TENSOR_PARALLELISM:=1

# Detect the architecture of the current machine
ARCH := $(shell uname -m)

# Define the Docker build command based on the architecture
ifeq ($(ARCH),arm64)
    DOCKER_BUILD_CMD := docker buildx build --platform linux/amd64
else
    DOCKER_BUILD_CMD := docker build
endif

# Check if TENANCY_NAME and REGION_KEY are set.
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

run.tgi.hf: check-env
	docker run --gpus all --shm-size 10gb \
		-p ${PORT}:${PORT} \
		-e TOKEN_FILE=${TARGET_TOKEN} \
		-e PARAMS=${PARAMS} \
		-e MODEL=${MODEL} \
		-v ${MODEL_DIR}:${TARGET_DIR} \
		-v ${TOKEN}:${TARGET_TOKEN} \
		${TGI_INFERENCE_IMAGE}$(shell cat version.txt)

run.tgi.oci: check-env
	docker run --gpus all --shm-size 10gb \
		-p ${PORT}:${PORT} \
		-e PARAMS=${PARAMS} \
		-e MODEL=${LOCAL_MODEL} \
		-v ${MODEL_DIR}:${TARGET_DIR} \
		${TGI_INFERENCE_IMAGE}$(shell cat version.txt)

run.vllm.hf: check-env
	docker run --gpus all --shm-size 10gb \
		-p ${PORT}:${PORT} \
		-e TOKEN_FILE=${TARGET_TOKEN} \
		-e MODEL=${MODEL} \
		-v ${MODEL_DIR}:${TARGET_DIR} \
		-v ${TOKEN}:${TARGET_TOKEN} \
		${VLLM_INFERENCE_IMAGE}$(shell cat version.txt)

run.vllm.oci: check-env
	docker run --rm -d --gpus all --shm-size 10gb \
		-e PORT=${PORT} \
		-e MODEL=${MODEL} \
		-v ${MODEL_DIR}:${LOCAL_MODEL} \
		${VLLM_INFERENCE_IMAGE}$(shell cat version.txt)

stop:
	docker stop $(shell docker ps -a -q)

rm:
	docker rm -f $(shell docker ps -a -q)

rmi:
	docker rmi -f $(shell docker images -a -q)

push.tgi: check-env
	docker push ${TGI_INFERENCE_IMAGE}$(shell cat version.txt)

push.vllm: check-env
	docker push ${VLLM_INFERENCE_IMAGE}$(shell cat version.txt)

app:
	MODEL=${model} gradio app.py
