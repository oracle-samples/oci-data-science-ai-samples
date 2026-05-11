# Multiple Inference Endpoints (MIE) code samples

These are samples for **Multiple Inference Endpoints**. It covers the following topics: API framework vs custom paths, invocation, create, update.

## Benefits (from product documentation)

- **Framework compatibility**: Set an API framework (for example `openai`) to allowlist standard paths so common LLM SDKs and tools work without listing each path.
- **Custom paths**: Up to **15** unique URI suffixes with **GET, POST, PUT, DELETE** where supported.
- **REST-style routing**: Use **`{}` in the suffix** as a one-segment path wildcard (for example `/models/{}` matches `/models/my-model`).

## Prerequisites

- A Data Science **project** and **compartment**.
- A **model** or **container image** ready to deploy; for BYOC the container listens on the configured port and implements each configured **`endpointUriSuffix`**.
- MIE is configured under **`environmentConfigurationDetails`** for both BYOC and service-managed containers.

## Two ways to configure endpoints

| Approach | SDK field | REST field | Notes |
|----------|-----------|------------|--------|
| **API framework** | `predict_api_specification` | `predictApiSpecification` | Value is **case-insensitive** (for example `openai`). Only **one** framework per deployment. |
| **Custom HTTP endpoints** | `custom_http_endpoints` | `customHttpEndpoints` | Optional **alongside** a framework. Use for paths not yet in the managed list (workaround until OCI adds them to the framework). |

Framework path lists for OpenAI live in [supported_endpoints](../supported_endpoints/README.md). For OpenAI SDK signing, see [openai_sdk_auth](../openai_sdk_auth/README.md).

## Layout

| Folder | Contents |
|--------|----------|
| [create_model_deployment](./create_model_deployment/) | Create a deployment with MIE (**Python SDK** or **REST JSON** + script). |
| [update_model_deployment](./update_model_deployment/) | Update MIE settings (**SDK** or **REST**). Rolling update: lifecycle moves to **UPDATING**, then **ACTIVE** when new routes are ready. |
| [inference](./inference/) | Signed `requests` examples (non-streaming and **SSE** streaming). |

---

## Create model deployment

- **SDK:** [create_model_deployment/sdk/create_mie_md.py](./create_model_deployment/sdk/create_mie_md.py)
- **REST:** Edit [create_model_deployment/api_payload/create_model_deployment.json](./create_model_deployment/api_payload/create_model_deployment.json) then run [create_model_deployment/api_payload/create_model_deployment_rest.py](./create_model_deployment/api_payload/create_model_deployment_rest.py).

The REST sample uses string values for `serverPort` / `healthCheckPort` as in the official API example; `customHttpEndpoints` includes both a fixed suffix and a `"/models/{}"` wildcard example.

---

## Update model deployment

Endpoint configuration can be updated on an **active** deployment without manual deactivation; URI suffix and framework changes trigger a **rolling update**.

- **SDK:** [update_model_deployment/sdk/update_mie_md.py](./update_model_deployment/sdk/update_mie_md.py)
- **REST:** Edit [update_model_deployment/api_payload/update_model_deployment.json](./update_model_deployment/api_payload/update_model_deployment.json) then run [update_model_deployment/api_payload/update_model_deployment_rest.py](./update_model_deployment/api_payload/update_model_deployment_rest.py).

---

## Inference URLs

When MIE is enabled, call the **registered suffix** after `/predict` (non-streaming) or `/predictWithResponseStream` (streaming):

| Mode | Pattern |
|------|---------|
| Standard | `https://<model-deployment-host>/<model-deployment-ocid>/predict/<suffix>` |
| Streaming | `https://<model-deployment-host>/<model-deployment-ocid>/predictWithResponseStream/<suffix>` |

**OpenAI chat completions example (non-streaming):**

`POST https://<host>/<ocid>/predict/v1/chat/completions`

Path and **query** parameters are supported; wildcards in the suffix map to dynamic path segments (see `/models/{}` above).

- **Non-streaming sample:** [inference/non_streaming/inference_mie.py](./inference/non_streaming/inference_mie.py)
- **Streaming sample:** [inference/streaming/inference_mie_streaming.py](./inference/streaming/inference_mie_streaming.py)

---
