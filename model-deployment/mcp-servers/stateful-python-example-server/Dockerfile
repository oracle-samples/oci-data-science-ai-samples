FROM python:3.13-slim

WORKDIR /app
RUN pip install uv
COPY mcp_simple_streamablehttp mcp_simple_streamablehttp
COPY pyproject.toml pyproject.toml
COPY README.md README.md
RUN uv sync

CMD ["uv", "--offline", "run", "mcp_simple_streamablehttp", "--port", "8080"]