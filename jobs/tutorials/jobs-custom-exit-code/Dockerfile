ARG type

FROM python:3.8-slim AS base

ENV DATASCIENCE_USER datascience
ENV DATASCIENCE_UID 1000
ENV HOME /home/$DATASCIENCE_USER

RUN python -m pip install \
    parse \
    oci


FROM base AS run-type-local
# nothing to see here

FROM base AS run-type-remote
COPY fail-with-code.py .
CMD ["python", "fail-with-code.py"]

FROM run-type-${type} AS final