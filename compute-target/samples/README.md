# Compute Target code samples

These are samples for **OCI Data Science Compute Targets**. They cover creating, updating, and deleting a Managed Compute Cluster Compute Target.

For model deployments that run on Compute Targets, see [model-deployment](../model-deployment/README.md).

## Prerequisites

- A Data Science **compartment**.
- OCI SDK authentication configured in `~/.oci/config`, or another config file/profile in the sample JSON. The samples use API key authentication by default. To use an OCI CLI session token, run `oci session authenticate` and set `auth` to `security_token`.
- Placeholder values in [sdk/config.example.json](./sdk/config.example.json) must be replaced before running the matching sample. For autoscaling queries, keep the literal `COMPUTE_TARGET_OCID` token unchanged.

Install the OCI Python SDK:

```bash
python3 -m pip install -r compute-target/samples/sdk/requirements.txt
```

## Layout

| File | Contents |
|------|----------|
| [sdk/config.example.json](./sdk/config.example.json) | Shared example config for Compute Target samples. Copy it to `config.json` before running. |
| [sdk/create_compute_target.py](./sdk/create_compute_target.py) | Create a Managed Compute Cluster Compute Target. |
| [sdk/update_compute_target.py](./sdk/update_compute_target.py) | Update Compute Target display metadata and tags. |
| [sdk/delete_compute_target.py](./sdk/delete_compute_target.py) | Delete a Compute Target. |

## Sample values

JSON does not support comments, so sample values are documented here instead of inside `config.example.json`.

| Field | Example value | Notes |
|-------|---------------|-------|
| `config_file` | `~/.oci/config` | OCI SDK config file path. |
| `profile_name` | `DEFAULT` | OCI SDK profile name. |
| `auth` | `api_key` | Use `api_key` for API key profiles or `security_token` for OCI CLI session-token profiles. |
| `instance_shape` | `VM.Standard.E4.Flex` | Use a shape supported for Data Science Compute Targets in your region. |
| `ocpus` | `10` | Flex shape OCPU count for Compute Target creation. |
| `memory_in_gbs` | `32` | Flex shape memory for Compute Target creation. |
| `boot_volume_size_in_gbs` | `100` | Boot volume size for Compute Target creation. |
| `scaling.type` | `AUTOSCALING` | The config example uses autoscaling by default. |

## Create Compute Target

Copy the example config and replace placeholder values:

```bash
cp compute-target/samples/sdk/config.example.json compute-target/samples/sdk/config.json
```

Print the SDK request payload without calling OCI:

```bash
python3 compute-target/samples/sdk/create_compute_target.py \
  --config-json compute-target/samples/sdk/config.json \
  --print-payload
```

Create the Compute Target and wait for the work request to finish:

```bash
python3 compute-target/samples/sdk/create_compute_target.py \
  --config-json compute-target/samples/sdk/config.json
```

When an autoscaling query needs the created Compute Target resource ID, use the literal `COMPUTE_TARGET_OCID` token in the `resourceId` filter. The service resolves it during create, so the sample sends the autoscaling policy directly in the create request.

Autoscaling query examples from the public doc:

```text
ComputeTargetUnschedulableWorkloadInstances[1m]{resourceId = "COMPUTE_TARGET_OCID"}.grouping().mean() > 0
ComputeTargetIdleInstances[1h]{resourceId = "COMPUTE_TARGET_OCID"}.grouping().mean() > 1
```

Fixed-size alternative:

```json
"scaling": {
  "type": "FIXED_SIZE",
  "instance_count": 1
}
```

## Update Compute Target

The Compute Target update sample updates display metadata and tags only. It does not include `computeConfigurationDetails`, so it avoids boot volume, shape, OCPU, and memory updates.

```bash
python3 compute-target/samples/sdk/update_compute_target.py \
  --config-json compute-target/samples/sdk/config.json \
  --print-payload
```

```bash
python3 compute-target/samples/sdk/update_compute_target.py \
  --config-json compute-target/samples/sdk/config.json
```

## Delete Compute Target

Delete model deployments before deleting the Compute Target they use. Delete samples require `--yes` for the actual delete call.

```bash
python3 compute-target/samples/sdk/delete_compute_target.py \
  --config-json compute-target/samples/sdk/config.json \
  --yes
```
