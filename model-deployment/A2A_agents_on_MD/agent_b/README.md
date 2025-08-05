# Agent B - Mumbai Weather Agent

An agent-to-agent communication system built with the A2A SDK that provides Mumbai weather information. This project demonstrates how to create a specialized agent that can communicate with other agents.

## Architecture

```
┌─────────────────┐    HTTP/A2A Protocol    ┌─────────────────┐
│   Agent A       │ ◄─────────────────────► │   Agent B       │
│ (External)      │                         │ (This Project)  │
│                 │                         │                 │
│ • Bengaluru     │                         │ • Mumbai        │
│   Weather       │                         │   Weather       │
│ • Comm. with    │                         │ • Weather Info  │
│   Agent B       │                         │   Return        │
└─────────────────┘                         └─────────────────┘
```


- **Mumbai Weather Information**: Provides current weather data for Mumbai
- **Agent-to-Agent Communication**: Seamless integration with other A2A-compatible agents
- **Docker Support**: Containerized deployment for easy scaling
- **Environment-Based Configuration**: Flexible configuration through environment variables

## Quick Start

```bash
# Install dependencies
uv sync

# Run the agent
uv run .
```

The agent will start on `http://localhost:9998` with the following endpoints:
- Health check: `GET /health`
- Agent card: `GET /a2a/.well-known/agent.json`
- Message handling: `POST /a2a/messages`

## Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `AGENT_B_URL` | URL for this agent's deployment | None | Yes |

## Exposed Endpoints

### Health Check
- **Endpoint**: `GET /health`
- **Response**: `{"status": "ok"}`
- **Purpose**: Kubernetes/load balancer health monitoring

### Agent Card
- **Endpoint**: `GET /a2a/.well-known/agent.json`
- **Purpose**: Provides agent metadata and capabilities for A2A protocol discovery

### Message Processing
- **Endpoint**: `POST /a2a/messages`
- **Purpose**: Handles incoming A2A protocol messages and returns Mumbai weather information

## Agent Capabilities

This agent specializes in Mumbai weather information with the following skill:

- **Skill ID**: `mumbai_weather`
- **Description**: Returns current Mumbai weather information
- **Tags**: `mumbai`, `weather`, `temperature`
- **Examples**:
  - "what is the weather in Mumbai?"
  - "get Mumbai weather"

## Docker Deployment

### Local Development
```bash
# Build the image
docker build -t agent-b .

# Run the container
docker run -p 9998:9998 \
  -e AGENT_B_URL="https://your-deployment-url.com/predict/a2a" \
  agent-b
```

### Oracle Cloud Infrastructure (OCI) Deployment

1. **Build and Push to OCIR**:
```bash
# Login to OCIR
docker login <region>.ocir.io

# Build and tag
docker build -t <region>.ocir.io/<tenancy>/<repo>/agent-b:latest .

# Push to OCIR
docker push <region>.ocir.io/<tenancy>/<repo>/agent-b:latest
```

2. **Deploy via OCI Model Deployment**:
   - Create a new Model Deployment in OCI Data Science
   - Use the pushed Docker image
   - Set environment variables in the deployment configuration
   - Configure the service to expose port 9998

### Environment Variables for OCI Deployment

When deploying to OCI Model Deployment service, configure these environment variables in the deployment settings:

```bash
AGENT_A_URL=https://your-model-deployment-url.com/predict/a2a
AGENT_B_URL=https://your-model-deployment-url.com/predict/a2a
```

## Development

## API Response Examples

### Health Check Response
```json
{
  "status": "ok"
}
```

### Agent Card Response
```json
{
  "name": "Mumbai Weather Agent",
  "description": "Just a Mumbai weather agent",
  "url": "https://your-deployment-url.com/predict/a2a",
  "version": "1.0.0",
  "defaultInputModes": ["text"],
  "defaultOutputModes": ["text"],
  "capabilities": {
    "streaming": true
  },
  "skills": [
    {
      "id": "mumbai_weather",
      "name": "Returns Mumbai weather information",
      "description": "just returns current Mumbai weather information",
      "tags": ["mumbai", "weather", "temperature"],
      "examples": [
        "what is the weather in Mumbai?",
        "get Mumbai weather"
      ]
    }
  ],
  "supportsAuthenticatedExtendedCard": false
}
```

### Weather Response
```
Mumbai Weather: 28°C, Partly Cloudy, Humidity: 75%, Wind: 12 km/h
```