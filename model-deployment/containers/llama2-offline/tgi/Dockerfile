FROM ghcr.io/huggingface/text-generation-inference:0.9.3
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get -y install tzdata && apt-get install -y curl
RUN pip install flask

WORKDIR /home/datascience
COPY start.sh start.sh
RUN chmod a+x start.sh
ENV PORT 8080
ENV MODEL /opt/ds/model/deployed_model
ENV PARAMS "--max-batch-prefill-tokens 1024"
EXPOSE ${PORT}
ENTRYPOINT [ "/bin/bash", "--login",  "-c"]
CMD ["/home/datascience/start.sh"]