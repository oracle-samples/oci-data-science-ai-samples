# Dockerfile
FROM python:latest

RUN pip install --no-cache-dir fastapi uvicorn[standard] requests httpx oracle-ads

WORKDIR /app
COPY signing_proxy.py /app/signing_proxy.py

EXPOSE 8080
CMD ["uvicorn", "signing_proxy:app", "--host", "0.0.0.0", "--port", "8080"]


