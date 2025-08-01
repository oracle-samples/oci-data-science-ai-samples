# Agent A - Bengaluru Weather Agent

An agent-to-agent communication system built with the A2A SDK that provides weather information for Bengaluru and collaborates with other agents to get Mumbai weather information. This project demonstrates how to create an intelligent agent that can communicate with other agents to gather and process information collaboratively.

## Architecture

```
┌─────────────────┐    HTTP/A2A Protocol    ┌─────────────────┐
│   Agent A       │ ◄─────────────────────► │   Agent B       │
│ (This Project)  │                         │ (External)      │
│                 │                         │                 │
│ • Bengaluru     │                         │ • Mumbai        │
│   Weather       │                         │   Weather       │
│                 │                         │                 │
│                 │                         │                 │
└─────────────────┘                         └─────────────────┘
```

## Quick Start

```bash
# Install dependencies
uv sync

# Run the agent
uv run .
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `AGENT_A_URL` | URL for this agent's deployment | Required |
| `AGENT_B_URL` | URL for the other agent to communicate with | Required |

## Exposed Endpoints

- `GET /health` - Health check endpoint
- `GET /a2a/.well-known/agent.json` - Agent card information
- `POST /a2a/messages` - Send messages to the agent

### Docker Deployment

```bash
# Build and run
docker build -t agent-a .
docker run -p 9999:9999 \
  -e AGENT_A_URL="https://your-deployment-url.com/predict/a2a" \
  -e AGENT_B_URL="https://your-deployment-url.com/predict/a2a" \
  agent-a
```

You can push this docker image to OCIR and then use Model Deployment service to run it. You can add the environment variables in the Model Deployment environment variables section.