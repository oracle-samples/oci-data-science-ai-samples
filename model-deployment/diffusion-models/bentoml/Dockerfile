FROM python:3.13-slim
RUN apt-get update -y
RUN apt-get install -y curl cmake
RUN apt-get install -y build-essential
RUN python3 -m pip install --upgrade pip
RUN pip install --upgrade torch transformers diffusers accelerate
RUN pip install bentoml Pillow protobuf peft sentencepiece oci
WORKDIR /opt/ds/model/deployed_model
CMD ["bentoml", "serve"]