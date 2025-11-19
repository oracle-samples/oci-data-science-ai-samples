# Homogeneous Model Group Deployment

Deploy multiple models together using OCI Data Science Model Groups for efficient multi-model serving from a single endpoint.

## What This Notebook Covers

- Building scikit-learn pipelines and registering models to the Model Catalog
- Creating homogeneous model groups with multiple models
- Deploying model groups to a single deployment endpoint
- Performing inference using model keys
- Live updates without downtime

## Prerequisites

- OCI Data Science project with Model Catalog access
- Python packages: `ads`, `oci` (≥2.163.0), `scikit-learn`, `pandas`, `requests`
- Environment variables: `PROJECT_OCID`, `NB_SESSION_COMPARTMENT_OCID`
- OCI config file or resource principal authentication
- Log group ID and log ID for deployment logging

## Quick Start

1. Open `homogeneous_model_group_deployment_example.ipynb` in your OCI Data Science notebook session
2. Set `project_id`, `compartment_id`, `access_log_group_id`, and `log_id`
3. Run cells sequentially

## Inference Example

Specify the model key in request headers to route to a specific model:

```python
headers = {
    'Content-Type': 'application/json',
    'model-key': 'svm1'  # Routes to specific model
}
response = requests.post(endpoint, json=data, auth=auth, headers=headers).json()
```

## Key Points

- **Homogeneous groups**: Models share the same framework, scoring script, and runtime
- **Model keys**: Each model has a unique inference key (e.g., "svm1", "svm2")
- **Common artifact**: Requires a shared `score.py` and `runtime.yaml` for dynamic model loading
- **Live updates**: Update deployments without downtime
- **OCI SDK**: Some Model Group features require OCI SDK directly (not fully supported in ADS SDK yet)
