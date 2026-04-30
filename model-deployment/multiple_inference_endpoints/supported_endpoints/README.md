# Supported Inference Endpoints

This page is the source of truth for the inference endpoints that OCI Data Science Model Deployment exposes when the **Multiple Inference Endpoints (MIE)** feature is enabled.

When you create or update a model deployment with MIE, you select an **inference API specification** (a "framework"). Once the framework is selected, the deployment automatically exposes the full set of endpoints that the framework supports, there is no need to enumerate them one by one in your deployment configuration.

The pages below describe the endpoints exposed by each supported framework.

## Supported Frameworks

| Framework | Identifier (`predict_api_specification`) | Documentation |
|-----------|------------------------------------------|---------------|
| OpenAI    | `openai`                                 | [OpenAI supported endpoints](./frameworks/openai/README.md) |

> More frameworks will be added over time. Each framework's documentation lives under [`./frameworks/<framework-name>/`](./frameworks/) and follows the same format.

## How the list is used

* When `predict_api_specification` is set to a supported framework on a model deployment, **all** endpoints listed for that framework become reachable on the deployment URL.
* You can additionally declare **custom endpoints** (`custom_http_endpoints`) on top of the framework-provided set. See the [API approach samples](../api_approach_samples/README.md) for examples.

## Related documentation

* [MIE — API Approach Samples](../api_approach_samples/README.md) — create / update a deployment and call MIE endpoints.
* [OpenAI SDK authentication samples](../openai_sdk_auth/README.md) — call OpenAI-compatible endpoints using the OpenAI Python SDK with OCI auth.