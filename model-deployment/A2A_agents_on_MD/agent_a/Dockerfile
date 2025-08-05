# syntax=docker/dockerfile:1
FROM ghcr.io/astral-sh/uv:debian

# Set work directory
WORKDIR /app

# Copy project files
COPY . .

# Install dependencies using uv (preferred for pyproject.toml)
RUN uv sync

# Expose the port the app runs on
EXPOSE 9999

# Run the app
CMD ["uv", "run", "."]