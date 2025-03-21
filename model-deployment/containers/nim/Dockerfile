FROM nvcr.io/nim/meta/llama3-8b-instruct:latest

USER root
RUN apt-get update
# curl package is needed to perform health checks on container
RUN apt-get -y install curl
COPY start.sh /opt/nim/start.sh
RUN chmod +x /opt/nim/start.sh

ENV NIM_CACHE_PATH /opt/ds/model/deployed_model
ENV NIM_SERVER_PORT 8080

# Known issue - https://docs.vllm.ai/en/latest/getting_started/troubleshooting.html#known-issues
ENV NCCL_CUMEM_ENABLE 0
EXPOSE ${NIM_SERVER_PORT}

ENTRYPOINT [ "/bin/bash", "--login",  "-c"]
CMD ["/opt/nim/start.sh"]