FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Copy local code to the container image.
COPY . /app

# Install pip dependencies
RUN pip install --upgrade pip \
    && pip install .

# Run the MCP Server
CMD ["python", "main.py"]
