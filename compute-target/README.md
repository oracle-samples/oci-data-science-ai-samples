# Compute Targets

Compute Targets let supported OCI Data Science workloads run on reusable managed compute capacity. This folder provides OCI Python SDK samples for:

- creating a Managed Compute Cluster Compute Target
- updating Compute Target metadata and tags
- deleting a Compute Target
- creating a model deployment that uses an existing Compute Target
- updating a model deployment on a Compute Target
- deleting a model deployment on a Compute Target

## Contents

| Path | Description |
|------|-------------|
| [samples](./samples/) | **Start here:** Python SDK samples for Compute Target create, update, and delete operations. |
| [model-deployment](./model-deployment/) | Python SDK samples for model deployments that run on Compute Targets. |

## Quick reference

- These samples use the **Managed Compute Cluster** Compute Target type.
- Create a Compute Target first, then create the model deployment that references its OCID.
- Replace placeholder values before running. For autoscaling queries, keep the backend-resolved resource ID tokens `COMPUTE_TARGET_OCID` and `MODEL_DEPLOYMENT_OCID` unchanged.
- For model deployments on Compute Targets, set explicit resource requests and limits so workload scheduling is predictable.
- The Compute Target update sample does not include compute configuration changes such as boot volume, shape, OCPU, or memory.
- The model deployment update sample does not update `computeTargetId` for active model deployments.
- Delete model deployments before deleting the Compute Target they use.
