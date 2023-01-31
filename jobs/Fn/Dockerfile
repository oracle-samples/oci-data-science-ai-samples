ARG type

FROM fnproject/python:3.8 as build-stage
WORKDIR /function
ADD requirements.txt /function/
RUN pip3 install --target /python/  --no-cache --no-cache-dir -r requirements.txt && \
	rm -fr ~/.cache/pip /tmp* requirements.txt func.yaml Dockerfile .venv
RUN pip3 install --target /python/ oci

ADD . /function/
RUN rm -fr /function/.pip_cache

FROM fnproject/python:3.8 AS base
# Configure jobs user and environment
ENV DATASCIENCE_USER datascience
ENV DATASCIENCE_UID 1000
ENV HOME /home/$DATASCIENCE_USER
ENV DATASCIENCE_INSTALL_DIR /etc/datascience

FROM base AS run-type-local
WORKDIR /function
COPY --from=build-stage /python /python
ENV PYTHONPATH=/python

FROM base AS run-type-job
WORKDIR /function
COPY --from=build-stage /python /python
COPY rp.py .
COPY jobrunner.py .
COPY testjobrunner.py .
ENV PYTHONPATH=/python
CMD ["python", "testjobrunner.py"]

FROM base AS run-type-fnl
WORKDIR /home
RUN mkdir -p datascience
RUN cd datascience
WORKDIR /home/datascience
RUN mkdir -p .oci
WORKDIR /home/datascience/.oci
COPY .oci/config .
COPY .oci/your-oci-private-key.pem .

WORKDIR /function
COPY --from=build-stage /python /python
COPY rp.py .
COPY jobrunner.py .
COPY func.py .
COPY func.yaml .
ENV PYTHONPATH=/python
ENTRYPOINT ["/python/bin/fdk", "/function/func.py", "handler"]

FROM base AS run-type-fn
WORKDIR /function
COPY --from=build-stage /python /python
COPY rp.py .
COPY jobrunner.py .
COPY func.py .
COPY func.yaml .
ENV PYTHONPATH=/python
ENTRYPOINT ["/python/bin/fdk", "/function/func.py", "handler"]

FROM run-type-${type} AS final