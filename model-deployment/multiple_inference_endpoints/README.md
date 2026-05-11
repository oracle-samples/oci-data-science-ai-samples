# Multiple Inference Endpoints (MIE)

OCI Data Science **model deployments** can expose **multiple HTTP inference paths** (OpenAI-compatible framework routes, custom suffixes, or both). This repository folder helps in quickly getting started with **Multiple Inference Endpoints**

## Contents

| Path | Description |
|------|-------------|
| [samples](./samples/) | **Start here:** create / update (Python SDK or REST JSON), plus signed HTTP inference examples. |
| [supported_endpoints](./supported_endpoints/) | **OpenAI** path list when `predict_api_specification` / `predictApiSpecification` is `openai`. |
| [openai_sdk_auth](./openai_sdk_auth/) | OpenAI Python SDK with OCI request signing. |

## Quick reference (from product documentation)

- **API framework**: e.g. `openai`: standard paths are allowlisted automatically; value is case-insensitive; **one framework per deployment**.
- **Custom HTTP endpoints**: Up to **15** suffixes; methods **GET, POST, PUT, DELETE**; use **`{}`** in the suffix for a single-segment wildcard.
- **Invocation**: `.../predict/<suffix>` (standard) or `.../predictWithResponseStream/<suffix>` (streaming).
- **BYOC**: Router strips **`/predict`** (or streaming prefix) before forwarding to the container on **serverPort** / **healthCheckPort**.
