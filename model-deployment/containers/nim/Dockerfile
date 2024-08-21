FROM nvcr.io/nim/meta/llama3-8b-instruct:latest

USER root
COPY start.sh /opt/nim/start.sh
RUN chmod +x /opt/nim/start.sh

ENV NIM_CACHE_PATH /opt/ds/model/deployed_model
ENV NIM_SERVER_PORT 8000
EXPOSE ${NIM_SERVER_PORT}

ENTRYPOINT [ "/bin/bash", "--login",  "-c"]
CMD ["/opt/nim/start.sh"]