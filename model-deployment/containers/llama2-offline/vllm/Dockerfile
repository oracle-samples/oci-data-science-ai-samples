FROM nvcr.io/nvidia/pytorch:22.12-py3
ENV DEBIAN_FRONTEND noninteractive
RUN pip uninstall -y torch
RUN pip install --upgrade pip
RUN pip install ninja psutil ray sentencepiece numpy
RUN pip install torch>=2.0.0
RUN pip install transformers>=4.28.0
RUN pip install xformers>=0.0.19
RUN pip install fastapi uvicorn
RUN pip install pydantic==1.10.11
RUN pip install fschat
RUN pip install GPUtil
RUN pip install vllm

# Default location where downloaded models are mapped on model container. No need to override.
ENV MODEL /opt/ds/model/deployed_model

# Tensor parallelism required by the model
ENV TENSOR_PARALLELISM 1

# Custom port for model container. No need to override.
ENV PORT 8080

WORKDIR /home/datascience
COPY api-server.py api-server.py
COPY start.sh /etc/start.sh
RUN chmod a+x /etc/start.sh
COPY log-config.yaml /etc/log-config.yaml
ENV UVICORN_LOG-CONFIG=/etc/log-config.yaml
ENV UVICORN_LOG_CONFIG=/etc/log-config.yaml
EXPOSE ${PORT}
ENTRYPOINT [ "/bin/bash", "--login",  "-c"]
CMD ["/etc/start.sh"]
