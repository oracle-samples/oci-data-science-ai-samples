FROM nvcr.io/nvidia/tritonserver:22.02-py3

HEALTHCHECK --start-period=15m --interval=30s --timeout=3s \
CMD curl -f localhost:5000/v2/health/ready || exit 1

# add key
RUN apt-key adv --fetch-keys https://developer.download.nvidia.com/compute/cuda/repos/ubuntu1804/x86_64/3bf863cc.pub

# install python 3.7
RUN add-apt-repository ppa:deadsnakes/ppa && apt-get install -y libpython3.7-dev

RUN pip install transformers
RUN pip install tensorflow

WORKDIR /opt/ds/model/deployed_model
COPY entrypoint.sh /
ENTRYPOINT []
RUN chmod +x /entrypoint.sh