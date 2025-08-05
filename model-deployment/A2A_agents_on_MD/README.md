# Agent-to-Agent (A2A) Communication on OCI Model Deployment

This project demonstrates a sophisticated agent-to-agent communication system deployed on Oracle Cloud Infrastructure (OCI) Model Deployment service. The system consists of two specialized agents that work together to provide comprehensive weather information through collaborative AI interactions.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│      Client Application                                         │
│         │                                                       │
│         ▼                                                       │
┌─────────────────────────────────────────────────────────────────┐
│                OCI Model Deployment Service                     │
│                                                                 │
│  ┌─────────────────┐                    ┌─────────────────┐     │
│  │   Agent A       │                    │   Agent B       │     │
│  │ (Primary Agent) │                    │ (Specialized)   │     │
│  │                 │                    │                 │     │
│  │ • Bengaluru     │◄─── A2A Protocol ─►│ • Mumbai        │     │
│  │   Weather       │                    │   Weather       │     │
│  │ • Orchestrates  │                    │ • Weather Info  │     │
│  │   Communication │                    │   Return        │     │
│  │ • Aggregates    │                    │                 │     │
│  │   Results       │                    │                 │     │
│  └─────────────────┘                    └─────────────────┘     │
└─────────────────────────────────────────────────────────────────┘
```

## System Capabilities

### Agent A (Primary Agent)
- **Role**: Orchestrator and aggregator
- **Responsibilities**:
  - Receives client requests for weather information
  - Provides Bengaluru weather information
  - Communicates with Agent B to retrieve Mumbai weather information
  - Aggregates and returns comprehensive weather data from both cities
- **Port**: 9999
- **Skills**: Bengaluru weather information and inter-agent communication

### Agent B (Specialized Agent)
- **Role**: Specialized weather provider
- **Responsibilities**:
  - Provides Mumbai weather information
  - Responds to A2A protocol requests from Agent A
  - Maintains focused expertise on Mumbai weather data
- **Port**: 9998
- **Skills**: Mumbai weather information and reporting

## Quick Start

### Prerequisites
- Oracle Cloud Infrastructure (OCI) account
- OCI CLI installed locally
- Python UV package manger: https://docs.astral.sh/uv/guides/install-python/
- Docker installed locally (for testing)
- Access to OCI Model Deployment service

### Local Development Setup

1. **Clone and navigate to the project**:
```bash
cd model-deployment/A2A_agents_on_MD/
```

2. **Set up Agent A**:
```bash
cd agent_a
uv sync
uv run .
```

3. **Set up Agent B** (in a separate terminal):
```bash
cd agent_b
uv sync
uv run .
```

## Docker Deployment

### Local Docker Testing

**Agent A**:
```bash
cd agent_a
docker build -t agent-a .
docker run -p 9999:9999 \
  -e AGENT_A_URL="http://localhost:9999/a2a" \
  -e AGENT_B_URL="http://localhost:9998/a2a" \
  agent-a
```

**Agent B**:
```bash
cd agent_b
docker build -t agent-b .
docker run -p 9998:9998 \
  -e AGENT_A_URL="http://localhost:9999/a2a" \
  -e AGENT_B_URL="http://localhost:9998/a2a" \
  agent-b
```

## OCI Model Deployment

### Step 1: Build and Push Docker Images

**For Agent A**:
```bash
# Login to OCIR
docker login <region>.ocir.io

# Build and tag
docker build -t <region>.ocir.io/<tenancy>/<repo>/agent-a:latest ./agent_a

# Push to OCIR
docker push <region>.ocir.io/<tenancy>/<repo>/agent-a:latest
```

**For Agent B**:
```bash
# Build and tag
docker build -t <region>.ocir.io/<tenancy>/<repo>/agent-b:latest ./agent_b

# Push to OCIR
docker push <region>.ocir.io/<tenancy>/<repo>/agent-b:latest
```

### Step 2: Deploy on OCI Model Deployment Service

1. **Deploy Agent B First**:
   - Navigate to OCI Data Science → Model Deployments
   - Create new deployment using the Agent B Docker image
   - Configure environment variables:
     ```
     AGENT_A_URL=https://<agent-a-deployment-url>/predict/a2a
     AGENT_B_URL=https://<agent-b-deployment-url>/predict/a2a
     CUSTOM_PREDICT_URL_ID=agent-b
     MODEL_DEPLOY_CUSTOM_ENDPOINTS=[{"endpointURI": "/a2a/", "httpMethods": ["POST"]},{"endpointURI": "/a2a", "httpMethods": ["POST"]},{"endpointURI": "/.well-known/agent.json", "httpMethods": ["GET"]},{"endpointURI": "/a2a/.well-known/agent.json", "httpMethods": ["GET"]},{"endpointURI": "/health", "httpMethods": ["GET"]}]
     WEB_CONCURRENCY=1
     ```
   - Set port to 9998
   - Deploy and note the deployment URL

2. **Deploy Agent A**:
   - Create new deployment using the Agent A Docker image
   - Configure environment variables:
     ```
     AGENT_A_URL=https://<agent-a-deployment-url>/predict/a2a
     AGENT_B_URL=https://<agent-b-deployment-url>/predict/a2a
     CUSTOM_PREDICT_URL_ID=agent-a
     MODEL_DEPLOY_CUSTOM_ENDPOINTS=[{"endpointURI": "/a2a/", "httpMethods": ["POST"]},{"endpointURI": "/a2a", "httpMethods": ["POST"]},{"endpointURI": "/.well-known/agent.json", "httpMethods": ["GET"]},{"endpointURI": "/a2a/.well-known/agent.json", "httpMethods": ["GET"]},{"endpointURI": "/health", "httpMethods": ["GET"]}]
     WEB_CONCURRENCY=1
     ```
   - Set port to 9999
   - Deploy

### Step 3: Configure Authentication

Both agents use OCI Resource Principal Signer (RPS) for authentication when deployed on OCI. The authentication is handled automatically by the A2A SDK in the Agent A code.

## Configuration

### Environment Variables

| Variable | Description |
|----------|-------------|
| `AGENT_A_URL` | Agent A's deployment URL |
| `AGENT_B_URL` | Agent B's deployment URL |
| `CUSTOM_PREDICT_URL_ID` | Custom URL identifier for Model Deployment |
| `MODEL_DEPLOY_CUSTOM_ENDPOINTS` | Custom endpoints configuration for A2A protocol |
| `WEB_CONCURRENCY` | Number of worker processes for web server |

### Port Configuration (in byoc panel)

- **Agent A**: Port 9999
- **Agent B**: Port 9998

## Usage Examples

### Using the Test Client (Recommended)

The `agent_a/test_client.py` file provides a complete example of how to interact with the A2A agents using OCI authentication.

```bash
# Navigate to agent_a directory
cd agent_a

# Run the test client
uv run python test_client.py
```

### Expected Response
```json
{
  "this_agent_result": "Bengaluru Weather: 25°C, Sunny, Humidity: 60%, Wind: 8 km/h",
  "other_agent_result": "Mumbai Weather: 28°C, Partly Cloudy, Humidity: 75%, Wind: 12 km/h"
}
```

---

**Note**: This is a demonstration system using dummy weather data. In production, replace the dummy data with real weather API integrations for accurate weather information.