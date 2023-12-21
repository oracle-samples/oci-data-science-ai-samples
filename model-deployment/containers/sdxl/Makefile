# Makefile for Stable Diffusion inference build, test and push
init:
	@if [ ! -f version.txt ]; then \
		echo 0 > version.txt; \
	fi

increment_version:
	@echo "Incrementing version..."
	@echo $$(($$(cat version.txt) + 1)) > version.txt

export TENANCY_NAME
export REGION_KEY

TENANCY:=${TENANCY_NAME}
CONTAINER_REGISTRY:=${REGION_KEY}.ocir.io

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
    DOCKER_BUILD_CMD := docker buildx build --platform linux/amd64 --target production
else
    DOCKER_BUILD_CMD := docker build --target production
endif

check-env:
	@if [ -z "$${TENANCY_NAME}" ] || [ -z "$${REGION_KEY}" ]; then \
		echo "TENANCY_NAME or REGION_KEY is not set or is empty"; \
		exit 1; \
	fi

build: check-env init increment_version
	$(DOCKER_BUILD_CMD) --network host \
	-t ${SDXL_INFERENCE_IMAGE}$(shell cat version.txt) \
	-f Dockerfile.sdxl .

run: check-env
	docker run --gpus all \
		-e TOKEN_FILE=/opt/ds/model/deployed_model/token \
		-e STORAGE_SIZE_IN_GB=500 \
		-p ${port}:${port} \
		-v $(shell pwd):/home/datascience/ \
		-v $(shell pwd)/token:/opt/ds/model/deployed_model/token \
		--shm-size=10gb \
		${SDXL_INFERENCE_IMAGE}$(shell cat version.txt)

stop: check-env
	docker stop $(shell docker ps -a -q)

remove: check-env
	docker rm $(shell docker ps -a -q)

push: check-env
	docker push ${SDXL_INFERENCE_IMAGE}$(shell cat version.txt)

app:
	MODEL=${model} gradio app.py
