ARG type

FROM python:3.10-slim AS base

ENV DATASCIENCE_USER datascience
ENV DATASCIENCE_UID 1000
ENV HOME /home/$DATASCIENCE_USER

# install required libraries
RUN python -m pip install \
        parse \
        oci

# python container does not have curl
RUN apt update
RUN apt-get install -y curl wget gpg git htop vim

FROM base AS run-type-local
# nothing to see here

FROM base AS run-type-remote
RUN mkdir -p /aiapps
COPY runner.sh /aiapps/
RUN chmod +x /aiapps/runner.sh

WORKDIR /aiapps
VOLUME /tmp

# Setup specific user, if required
# RUN useradd -ms /bin/bash appuser
# USER appuser

ENTRYPOINT ["/aiapps/runner.sh"]

FROM run-type-${type} AS final