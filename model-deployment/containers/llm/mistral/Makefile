TENANCY:=${TENANCY_NAME}
CONTAINER_REGISTRY:=${REGION_KEY}.ocir.io

TGI_INFERENCE_IMAGE:=${CONTAINER_REGISTRY}/${TENANCY}/text-generation-interface-odsc:0.9.3
TGI_CONTAINER_NAME:=tgi-odsc

VLLM_INFERENCE_IMAGE:=${CONTAINER_REGISTRY}/${TENANCY}/vllm-odsc:0.2.0
VLLM_CONTAINER_NAME:=vllm-odsc

GRADIO_IMAGE:=${CONTAINER_REGISTRY}/${TENANCY}/gradio-odsc:0.1.0
GRADIO_CONTAINER_NAME:=gradio-odsc

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

VLLM:=1
API_SPEC:=openai

IAM_TYPE:=security_token
IAM_PROFILE:=custboat

build.app:
	docker build --network host -t ${GRADIO_IMAGE} -f Dockerfile.gradio .
run.app.vllm:
	docker run --rm --network host -e OCI_IAM_TYPE=${IAM_TYPE} -e OCI_CONFIG_PROFILE=${IAM_PROFILE} -e MODEL=${model} -e VLLM=${VLLM} -e API_SPEC=${API_SPEC} --name ${GRADIO_CONTAINER_NAME}  ${GRADIO_IMAGE}
run.app.tgi:
	docker run --rm --network host -e OCI_IAM_TYPE=${IAM_TYPE} -e OCI_CONFIG_PROFILE=${IAM_PROFILE} -e MODEL=${model} --name ${GRADIO_CONTAINER_NAME}  ${GRADIO_IMAGE}
app:
	MODEL=${model} gradio app.py
push.app:
	docker push ${GRADIO_IMAGE}