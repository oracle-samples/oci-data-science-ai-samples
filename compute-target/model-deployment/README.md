# Model Deployment On Compute Target

OCI Data Science model deployments can run on an existing Managed Compute Cluster Compute Target. This folder provides Python SDK samples for creating, updating, and deleting model deployments that use Compute Target infrastructure.

## Contents

| Path | Description |
|------|-------------|
| [samples](./samples/) | **Start here:** Python SDK samples for model deployment operations on a Compute Target. |

## Quick reference

- Create the Compute Target before creating a model deployment that references it.
- The model deployment create sample sets `computeTargetId`.
- The model deployment update sample does not set `computeTargetId`, because active model deployments on Compute Targets do not support updating that field.
- Delete model deployments before deleting the Compute Target they use.
