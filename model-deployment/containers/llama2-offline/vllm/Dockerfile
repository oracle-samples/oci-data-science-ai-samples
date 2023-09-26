FROM nvidia/cuda:11.8.0-base-ubuntu20.04 as base
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get -y install tzdata && apt-get install -y nginx && apt-get install -y curl && apt-get install -y git
RUN curl -L https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh >> miniconda.sh
RUN bash ./miniconda.sh -b -p /miniconda; rm ./miniconda.sh;
ENV PATH="/miniconda/bin:$PATH"
RUN mkdir -p /opt/vllm

ARG INSTALL_DIR=/opt/vllm
COPY vllm-env.yaml /opt/vllm/environment.yaml
RUN conda env create --name vllm -f ${INSTALL_DIR}/environment.yaml

ENV TMPDIR=/home/datascience
WORKDIR /home/datascience

# Default location where downloaded models are mapped on model container. No need to override.
ENV MODEL /opt/ds/model/deployed_model

# Tensor parallelism required by the model
ENV TENSOR_PARALLELISM 1

# Custom port for model container. No need to override.
ENV PORT 8080

COPY api-server.py api-server.py
COPY start.sh /etc/start.sh
RUN chmod a+x /etc/start.sh
COPY log-config.yaml /etc/log-config.yaml
ENV UVICORN_LOG-CONFIG=/etc/log-config.yaml
ENV UVICORN_LOG_CONFIG=/etc/log-config.yaml
EXPOSE ${PORT}
ENTRYPOINT [ "/bin/bash", "--login",  "-c"]
CMD ["/etc/start.sh"]