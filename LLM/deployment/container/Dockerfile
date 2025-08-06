FROM ghcr.io/oracle/oraclelinux:9-slim

RUN curl -L -o ./miniconda.sh -O https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh \
    && chmod +x ./miniconda.sh \
    && ./miniconda.sh -b -p /opt/conda \
    && rm ./miniconda.sh \
    && echo ". /opt/conda/etc/profile.d/conda.sh" >> ~/.bashrc \
    && /opt/conda/bin/conda update python cryptography \
    && /opt/conda/bin/conda clean -ya

RUN microdnf install -y expat-devel which wget && microdnf clean all

ARG USERNAME=uwsgi
RUN useradd -ms /bin/bash $USERNAME
USER $USERNAME
WORKDIR /home/$USERNAME

# Create conda env
RUN /opt/conda/bin/conda create -n conda_env python=3.10 pip -y
SHELL ["/opt/conda/bin/conda", "run", "-n", "conda_env", "/bin/bash", "-c"]

COPY requirements.txt /opt/requirements.txt
RUN pip install -r /opt/requirements.txt && pip cache purge
COPY app.py /opt/app.py

ENV MODEL_DIR="/opt/ds/model/deployed_model"
ENV PATH=/home/$USERNAME/.conda/envs/conda_env/bin:/opt/conda/bin/:$PATH
ENTRYPOINT [ "uwsgi" ]
CMD [ "--http", "0.0.0.0:8080", "--master", "--enable-threads", "--single-interpreter", "-p", "5", "--chdir", "/opt", "--module", "app:app" ]
