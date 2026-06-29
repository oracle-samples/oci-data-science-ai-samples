# Model Deployment On Compute Target code samples

These are samples for **OCI Data Science model deployments on Compute Targets**. They cover creating, updating, and deleting a `SINGLE_MODEL_FLEX` model deployment that runs on an existing Managed Compute Cluster Compute Target.

## Prerequisites

- A Data Science **compartment** and **project**.
- An existing Data Science **Compute Target OCID**.
- A **model OCID** and an inference container image.
- OCI SDK authentication configured in `~/.oci/config`, or another config file/profile in the sample JSON. The samples use API key authentication by default. To use an OCI CLI session token, run `oci session authenticate` and set `auth` to `security_token`.
- Replace placeholder values in [sdk/config.example.json](./sdk/config.example.json) before running the matching sample. For autoscaling queries, keep the literal `MODEL_DEPLOYMENT_OCID` token unchanged.

Install the OCI Python SDK:

```bash
python3 -m pip install -r compute-target/model-deployment/samples/sdk/requirements.txt
```

## Layout

| File | Contents |
|------|----------|
| [sdk/config.example.json](./sdk/config.example.json) | Shared example config for model deployment samples. Copy it to `config.json` before running. |
| [sdk/create_model_deployment_on_compute_target.py](./sdk/create_model_deployment_on_compute_target.py) | Create a model deployment on an existing Compute Target. |
| [sdk/update_model_deployment_on_compute_target.py](./sdk/update_model_deployment_on_compute_target.py) | Update model, environment, resource, scaling, display metadata, and tags. |
| [sdk/delete_model_deployment_on_compute_target.py](./sdk/delete_model_deployment_on_compute_target.py) | Delete a model deployment on a Compute Target. |

## Sample values

JSON does not support comments, so sample values are documented here instead of inside `config.example.json`.

| Field | Example value | Notes |
|-------|---------------|-------|
| `auth` | `api_key` | Use `api_key` for API key profiles or `security_token` for OCI CLI session-token profiles. |
| `server_port` | `8080` | Container server port for model deployment create or update. |
| `health_check_port` | `8080` | Container health check port for model deployment create or update. |
| `resource_request.ocpus` | `1` | Workload CPU request for model deployment scheduling. |
| `resource_request.memory_in_gbs` | `6` | Workload memory request for model deployment scheduling. |
| `resource_limit.ocpus` | `2` | Workload CPU limit. Keep it greater than or equal to the request. |
| `resource_limit.memory_in_gbs` | `12` | Workload memory limit. Keep it greater than or equal to the request. |
| `scaling.type` | `AUTOSCALING` | The config example uses autoscaling by default. |
| `scaling.autoscaling.minimum_instance_count` | `1` | Use at least one instance. The service rejects `initial_instance_count` set to `0` for this model deployment autoscaling shape. |
| `container_image` | `dsmc://odsc-vllm-serving:<image_version>` | Use the service-managed vLLM image format from the public doc, or a valid BYOC image URI such as `iad.ocir.io/<namespace>/<repository>:<tag>`. |

## Scaling shape

The config example uses custom-expression autoscaling with the backend-resolved resource ID token `MODEL_DEPLOYMENT_OCID`:

```json
"scaling": {
  "type": "AUTOSCALING",
  "autoscaling": {
    "minimum_instance_count": 1,
    "maximum_instance_count": 3,
    "initial_instance_count": 1,
    "rules": [
      {
        "type": "TARGET_CUSTOM_EXPRESSION",
        "query": "CpuUtilization[1m]{resourceId = \"MODEL_DEPLOYMENT_OCID\"}.grouping().mean()",
        "threshold": 70.0
      },
      {
        "type": "TARGET_CUSTOM_EXPRESSION",
        "query": "PredictRequestCount[1h]{resourceId = \"MODEL_DEPLOYMENT_OCID\"}.grouping().sum()",
        "threshold": 1.0
      }
    ],
    "scale_out_policy": {
      "pending_duration": "PT1M",
      "instance_count_adjustment": 1,
      "cool_down_in_seconds": 300
    },
    "scale_in_policy": {
      "pending_duration": "PT10M",
      "instance_count_adjustment": 1,
      "cool_down_in_seconds": 300
    }
  }
}
```

When an autoscaling query needs the model deployment resource ID, use the literal `MODEL_DEPLOYMENT_OCID` token in the `resourceId` filter. The service resolves it, so the create and update samples send the scaling policy directly.

Predefined metric autoscaling example:

```json
"scaling": {
  "type": "AUTOSCALING",
  "autoscaling": {
    "minimum_instance_count": 1,
    "maximum_instance_count": 3,
    "initial_instance_count": 1,
    "rules": [
      {
        "type": "TARGET_PREDEFINED_EXPRESSION",
        "metric_type": "CPU_UTILIZATION",
        "threshold": 70.0
      }
    ],
    "scale_out_policy": {
      "pending_duration": "PT1M",
      "instance_count_adjustment": 1,
      "cool_down_in_seconds": 300
    },
    "scale_in_policy": {
      "pending_duration": "PT10M",
      "instance_count_adjustment": 1,
      "cool_down_in_seconds": 300
    }
  }
}
```

Fixed-size alternative:

```json
"scaling": {
  "type": "FIXED_SIZE",
  "instance_count": 1
}
```

## Create model deployment

```bash
cp compute-target/model-deployment/samples/sdk/config.example.json \
  compute-target/model-deployment/samples/sdk/config.json
```

Replace the placeholder values in `config.json` before running the sample.

```bash
python3 compute-target/model-deployment/samples/sdk/create_model_deployment_on_compute_target.py \
  --config-json compute-target/model-deployment/samples/sdk/config.json \
  --print-payload
```

```bash
python3 compute-target/model-deployment/samples/sdk/create_model_deployment_on_compute_target.py \
  --config-json compute-target/model-deployment/samples/sdk/config.json
```

## Update model deployment

The update sample omits `computeTargetId` because active model deployments on Compute Targets do not support updating that field.

Example runtime values from the public doc:

```text
DEPLOYMENT_SCHEDULING_TIMEOUT=30
ENABLE_REQUEST_BUFFERING=true
```

```bash
python3 compute-target/model-deployment/samples/sdk/update_model_deployment_on_compute_target.py \
  --config-json compute-target/model-deployment/samples/sdk/config.json \
  --print-payload
```

```bash
python3 compute-target/model-deployment/samples/sdk/update_model_deployment_on_compute_target.py \
  --config-json compute-target/model-deployment/samples/sdk/config.json
```

## Delete model deployment

Delete samples require `--yes` for the actual delete call.

```bash
python3 compute-target/model-deployment/samples/sdk/delete_model_deployment_on_compute_target.py \
  --config-json compute-target/model-deployment/samples/sdk/config.json \
  --yes
```
