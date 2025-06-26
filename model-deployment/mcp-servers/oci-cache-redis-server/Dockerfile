FROM python:3.13-slim
RUN pip install --upgrade uv

WORKDIR /app
COPY . /app
RUN uv sync

CMD ["uv", "--offline", "run", "python", "src/main.py"]
