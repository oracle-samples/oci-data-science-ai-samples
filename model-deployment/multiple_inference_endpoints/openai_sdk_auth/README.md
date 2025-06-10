# OCI OpenAI SDK Auth

This folder demonstrates how to use a custom authentication layer to enable OpenAI SDK compatibility with Oracle Cloud Infrastructure (OCI) Data Science Model Deployments, including support for streaming and non-streaming endpoints.

## Overview

The `oci_openai_auth` module provides a custom authentication class and a drop-in replacement for the OpenAI client, allowing you to use the OpenAI Python SDK with OCI model deployments that require request signing.

### Key Components

- **`oci_openai_auth/signer_auth_override.py`**  
  Contains:
  - `MyCustomAuth`: An `httpx.Auth` implementation that signs requests using OCI's security token and private key.
  - `MultiInferOpenAI`: A subclass of `openai.OpenAI` that injects the custom authentication into all requests, making it compatible with OCI endpoints.

- **`local_custom_auth.py`**  
  Example script for using the custom OpenAI client with a standard (non-streaming) OCI model deployment endpoint.

- **`local_custom_auth_streaming.py`**  
  Example script for using the custom OpenAI client with a streaming OCI model deployment endpoint.

## Installation

Ensure you have the following dependencies installed:
- `oci`
- `openai`
- `httpx`
- `requests`

You can install them via pip:
```bash
pip install oci openai httpx requests
```

## Usage

### 1. Prepare OCI Config

Make sure your `~/.oci/config` is set up with a valid profile, and that the profile includes a `security_token_file` and `key_file`.

### 2. Using the Custom OpenAI Client

#### Non-Streaming Example

See `local_custom_auth.py` for a full example. The key steps are:

```python
from oci_openai_auth.signer_auth_override import MultiInferOpenAI

# Get OCI signer (see local_custom_auth.py for details)
signer = get_oci_signer()

# Set your model deployment OCID and endpoint
mdocid = '<your-model-deployment-ocid>'
predict_endpoint = f'https://<host>:<port>/{mdocid}/predict/v1'

# Initialize the custom OpenAI client
custom_oci_openai = MultiInferOpenAI(
    oci_signer=signer,
    api_key='',
    base_url=predict_endpoint
)

# Make a chat completion request
response = custom_oci_openai.chat.completions.create(
    model='/opt/ds/model/deployed_model',
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Tell me something interesting."}
    ],
    max_tokens=500
)
print(response)
```

#### Streaming Example

See `local_custom_auth_streaming.py` for a full example. The main difference is the endpoint and the use of `stream=True`:

```python
predict_streaming_endpoint = f'https://<host>:<port>/{mdocid}/predictWithResponseStream/v1'

custom_oci_openai = MultiInferOpenAI(
    oci_signer=signer,
    api_key='',
    base_url=predict_streaming_endpoint
)

response = custom_oci_openai.chat.completions.create(
    model='/opt/ds/model/deployed_model',
    messages=[{"role": "user", "content": "Stream me a story."}],
    stream=True,
    max_tokens=1000
)

for chunk in response:
    delta = chunk.choices[0].delta.content
    if delta:
        print(delta, end="", flush=True)
```

## How it Works

- The custom `MyCustomAuth` class signs each HTTP request using OCI's security token and private key.
- `MultiInferOpenAI` injects this authentication into all OpenAI SDK requests, making it seamless to use OpenAI SDK methods with OCI endpoints.

## Notes

- SSL verification is disabled by default for local testing. **Remove or set `verify=True` in production.**
- Logging is set to DEBUG for detailed output; adjust as needed.
- The scripts assume you have a deployed model in OCI Data Science and the correct permissions.