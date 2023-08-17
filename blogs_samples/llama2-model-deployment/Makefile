TENANCY:=<placeholder>
CONTAINER_REGISTRY:=<placeholder.ocir.io>

TGI_INFERENCE_IMAGE:=${CONTAINER_REGISTRY}/${TENANCY}/text-generation-interface-odsc:0.9.3
TGI_CONTAINER_NAME:=tgi-odsc

VLLM_INFERENCE_IMAGE:=${CONTAINER_REGISTRY}/${TENANCY}/vllm-odsc:0.1.3
VLLM_CONTAINER_NAME:=vllm-odsc

MODEL_DIR:=${PWD}/hfdata
TARGET_DIR:=/home/datascience
HF_DIR=/home/datascience/.cache

token:=${PWD}/token
target_token:=/opt/ds/model/deployed_model/token
model:=meta-llama/Llama-2-7b-chat-hf

build.tgi:
	docker build --network host -t ${TGI_INFERENCE_IMAGE} .
build.vllm:
	docker build --network host -t ${VLLM_INFERENCE_IMAGE} -f Dockerfile.vllm .
run.tgi:
	docker run --rm -it --gpus all --shm-size 1g -p 5001:5001 -e TOKEN_FILE=${target_token} -e PARAMS="--model-id ${model}" -v ${MODEL_DIR}:${TARGET_DIR} -v ${token}:${target_token} --name ${TGI_CONTAINER_NAME} ${TGI_INFERENCE_IMAGE}  
run.vllm:
	docker run --rm -d --gpus all --shm-size 1g -p 5001:5001 -e UVICORN_NO_USE_COLORS=1 -e TOKEN_FILE=${target_token} -e PARAMS="--model ${model}" -e HUGGINGFACE_HUB_CACHE=${HF_DIR} -v ${MODEL_DIR}:${TARGET_DIR} -v ${token}:${target_token} --name ${VLLM_CONTAINER_NAME} ${VLLM_INFERENCE_IMAGE}  
stop.tgi:
	docker stop ${TGI_CONTAINER_NAME}
stop.vllm:
	docker stop ${VLLM_CONTAINER_NAME}	
shell.tgi:
	docker run --rm -it --shm-size=1g --net host -p 5001:5001 -e TOKEN_FILE=${target_token} -e PARAMS="--model-id ${model}" --entrypoint bash -v ${MODEL_DIR}:${TARGET_DIR} -v ${token}:${target_token} --name ${TGI_CONTAINER_NAME} ${TGI_INFERENCE_IMAGE} 
shell.vllm:
	docker run --rm -it --shm-size=1g --net host -p 5001:5001 -e TOKEN_FILE=${target_token} -e PARAMS="--model ${model}" -e HUGGINGFACE_HUB_CACHE=${HF_DIR} --entrypoint bash -v ${MODEL_DIR}:${TARGET_DIR} -v ${token}:${target_token} --name ${VLLM_CONTAINER_NAME} ${	docker run --rm -d --gpus all --shm-size 1g -p 5001:5001 -e UVICORN_NO_USE_COLORS=1 -e TOKEN_FILE=${target_token} -e PARAMS="--model ${model}" -e HUGGINGFACE_HUB_CACHE=${HF_DIR} -v ${MODEL_DIR}:${TARGET_DIR} -v ${token}:${target_token} --name ${VLLM_CONTAINER_NAME} ${VLLM_INFERENCE_IMAGE}  
} 
push.tgi:
	docker push ${TGI_INFERENCE_IMAGE}
push.vllm:
	docker push ${VLLM_INFERENCE_IMAGE}	
app:
	MODEL=${model} gradio app.py

