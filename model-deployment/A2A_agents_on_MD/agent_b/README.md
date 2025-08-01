# Agent B - OCI Realm Finder Agent

An agent-to-agent communication system built with the A2A SDK that provides dummy OCI realm status. This project demonstrates how to create a specialized agent that can communicate with other agents.

## Architecture

```
┌─────────────────┐    HTTP/A2A Protocol    ┌─────────────────┐
│   Agent A       │ ◄─────────────────────► │   Agent B       │
│ (External)      │                         │ (This Project)  │
│                 │                         │                 │
│ • Status        │                         │ • OCI Realm     │
│   Reporter      │                         │   Finder        │
│ • Comm. with    │                         │ • Realm Status  │
│   Agent B       │                         │   Return        │
└─────────────────┘                         └─────────────────┘
```


- **OCI Realm Status Monitoring**: Provides real-time status of OCI realms (OC1, OC2, OC3)
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
- **Purpose**: Handles incoming A2A protocol messages and returns OCI realm status

## Agent Capabilities

This agent specializes in OCI realm status monitoring with the following skill:

- **Skill ID**: `oci_realm_finder`
- **Description**: Returns OCI functioning realms and their status
- **Tags**: `oci`, `realm`, `finder`
- **Examples**:
  - "what are the functioning realms and their status?"
  - "what is the status of the OCI-1 realm?"

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
  "name": "OCI Realm Finder Agent",
  "description": "Just a OCI realm finder agent",
  "url": "https://your-deployment-url.com/predict/a2a",
  "version": "1.0.0",
  "defaultInputModes": ["text"],
  "defaultOutputModes": ["text"],
  "capabilities": {
    "streaming": true
  },
  "skills": [
    {
      "id": "oci_realm_finder",
      "name": "Returns OCI functioning realms and their status",
      "description": "just returns OCI functioning realms and their status",
      "tags": ["oci", "realm", "finder"],
      "examples": [
        "what are the functioning realms and their status?",
        "what is the status of the OCI-1 realm?"
      ]
    }
  ],
  "supportsAuthenticatedExtendedCard": false
}
```

### Realm Status Response
```
🟨 Old Realms status 🟨: OC1 ✅, OC2 ✅, OC3 ✅
```