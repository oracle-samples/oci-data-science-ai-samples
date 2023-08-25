FROM ghcr.io/huggingface/text-generation-inference:0.9.3
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get -y install tzdata && apt-get install -y curl
RUN pip install flask

WORKDIR /home/datascience
COPY start.sh start.sh
RUN chmod a+x start.sh
ENV PORT 8080
ENV MODEL /opt/ds/model/deployed_model

# llama2-7b-hf
ENV PARAMS "--max-batch-prefill-tokens 1024"

# llama2-13b-hf
# ENV PARAMS "--max-batch-prefill-tokens 1024 --quantize bitsandbytes --max-batch-total-tokens 4096"

EXPOSE ${PORT}
ENTRYPOINT [ "/bin/bash", "--login",  "-c"]
CMD ["/home/datascience/start.sh"]