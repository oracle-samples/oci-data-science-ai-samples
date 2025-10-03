# Description
OCI Generative AI Agents is a fully managed service that combines the power of large language models (LLMs) with AI technologies to create intelligent virtual agents that can provide personalized, context-aware, and highly engaging customer experiences.

The OCI Agent Development Kit (ADK) is a client-side library that simplifies building agentic applications on top of OCI Generative AI Agents Service.
When pairing the ADK with OCI Generative AI Agents Service, you can use simple but powerful primitives to build complex, production-grade agentic applications.

In this document, we will use mcp tool integration of [ADK library](https://agents.oraclecorp.com/adk/examples/agent-mcp-tool) to connect to remote hosted agent on model deployment service.

# Prerequisites

- Install pip dependencies mentioned in [requirements.txt](./requirements.txt)
```
pip install -r requirements.txt
```

- Create OCI session and populate your local OCI config files with valid [session details](https://docs.oracle.com/en-us/iaas/Content/API/SDKDocs/clitoken.htm)
```
oci session authenticate
```

- Start [mcp_client.py](./mcp_client.py)
```
python3 mcp_client.py
```