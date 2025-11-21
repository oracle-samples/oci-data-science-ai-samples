# Multiple Inference Endpoints (MIE) - API Approach Samples

## Overview

Oracle Cloud Infrastructure (OCI) Data Science now supports **Multiple Inference Endpoints (MIE)**, allowing you to expose your model deployments at custom endpoints beyond the standard `/predict` endpoint. This feature enables you to:

- **Use OpenAI-compatible API specifications**
- **Define custom endpoints** tailored to your specific use cases



## Prerequisites

Before you begin, ensure you have:

1. **OCI SDK for Python** installed (currently supported in preview sdk version)
   ```bash
   pip install --trusted-host=artifactory.oci.oraclecorp.com -i https://artifactory.oci.oraclecorp.com/api/pypi/global-dev-pypi/simple -U oci==2.160.2+preview.1.278
   ```

2. **OCI Configuration** set up
   - A valid OCI config file at `~/.oci/config`
   - Required credentials: tenancy, user, fingerprint, key_file, and optionally pass_phrase
   - For security token authentication: `security_token_file` configured

3. **Additional dependencies** (for streaming inference)
   ```bash
   pip install sseclient-py requests
   ```

4. **Required OCIDs**:
   - Project OCID
   - Compartment OCID
   - Model OCID (if creating a new deployment)


## Quick Start

### Step 1: Create a Model Deployment with Multiple Endpoints

Use `create_mie_md.py` to create a model deployment with custom inference endpoints:

```python
python create_mie_md.py
```

**Key Configuration Options:**

- **`predict_api_specification`**: Set to `"openai"` for OpenAI-compatible endpoints
- **`custom_http_endpoints`**: Define custom endpoint URI suffixes and supported HTTP methods
  ```python
  custom_http_endpoints=[
      oci.data_science.models.InferenceHttpEndpoint(
          endpoint_uri_suffix="/v1/custom/completions",
          http_methods=[HTTPMethod.GET, HTTPMethod.POST]
      )
  ]
  ```

**Before running**, update the following in `create_mie_md.py`:
- `project_id`: Your Data Science project OCID
- `compartment_id`: Your compartment OCID
- `model_id`: Your model OCID
- `image` and `image_digest`: Your container image details
- `display_name` and `description`: Descriptive names for your deployment

### Step 2: Update an Existing Model Deployment

Use `update_mie_md.py` to modify an existing model deployment's endpoints:

```python
python update_mie_md.py
```

**Before running**, update:
- `model_deployment_id`: The OCID of your existing model deployment
- Any configuration parameters you wish to modify (endpoints, API specification, etc.)

### Step 3: Make Inference Calls

#### Standard (Non-Streaming) Inference

Use `inference_mie.py` for standard inference calls:

```python
python inference_mie.py
```

**Before running**, update:
- `endpoint`: Your model deployment endpoint URL (e.g., `https://<deployment-id>.modeldeployment.<region>.oci.customer-oci.com/v1/your/endpoint`)
- `body`: Your inference request payload

#### Streaming Inference

Use `inference_mie_streaming.py` for Server-Sent Events (SSE) streaming inference:

```python
python inference_mie_streaming.py
```

