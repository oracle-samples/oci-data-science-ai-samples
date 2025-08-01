FROM ghcr.io/astral-sh/uv:debian

WORKDIR /app

COPY . .

RUN uv sync

EXPOSE 9998

CMD ["uv", "run", "."]