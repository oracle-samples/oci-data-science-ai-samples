TENANCY:=${TENANCY_NAME}
CONTAINER_REGISTRY:=${REGION_KEY}.ocir.io

TGI_INFERENCE_IMAGE:=${CONTAINER_REGISTRY}/${TENANCY}/tgi-odsc:1.0.0
TGI_CONTAINER_NAME:=tgi-odsc

SOURCE_MODEL_DIR=/model
TARGET_MODEL_DIR=/opt/ds/model/deployed_model
PORT=9090

build:
	docker build -t ${TGI_INFERENCE_IMAGE} -f Dockerfile .

push:
	docker push ${TGI_INFERENCE_IMAGE}

run:
	docker run -e PORT=${PORT} -e MODEL=${TARGET_MODEL_DIR} --shm-size=1gb -p ${PORT}:${PORT} -v ${SOURCE_MODEL_DIR}:${TARGET_MODEL_DIR}:Z -it --gpus all ${TGI_INFERENCE_IMAGE}