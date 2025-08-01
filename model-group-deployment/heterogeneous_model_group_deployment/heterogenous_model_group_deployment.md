# Heterogeneous Model Group Deployment

## Description

A **Heterogeneous Model Group** comprises models built on different ML frameworks, such as PyTorch, TensorFlow, ONNX, etc. This group type allows for the deployment of diverse model architectures within a single serving environment.

> ℹ️ Heterogeneous model groups **do not** require a shared model group artifact, as models in the group may rely on different runtimes.

## Use Case

Ideal for scenarios requiring multiple models with different architectures or frameworks deployed together under a unified endpoint.

## Supported Containers

- **BYOC (Bring Your Own Container)** that satisfies the **BYOC Contract** requirements.
- Customers are encouraged to use **NVIDIA Triton Inference Server**, which provides built-in support for diverse frameworks.

## Serving Mechanism

- Customers should use the **BYOC** deployment flow.
- **NVIDIA Triton Inference Server** is recommended for hosting models built with PyTorch, TensorFlow, ONNX Runtime, Custom Python, etc.
- Each model is routed to its corresponding backend automatically.
- **Triton** handles load balancing, routing, and execution optimization across model types.

For details on dependency management, refer to the section [Dependency Management for Heterogeneous Model Group](#dependency-management-for-heterogeneous-model-group).

## Heterogeneous Model Group Structure

```json
{
  "modelGroupsDetails": {
    "modelGroupConfigurationDetails": {
      "modelGroupType": "HETEROGENEOUS"
    },
    "modelIds": [
      {
        "inferenceKey": "model1",
        "modelId": "ocid.datasciencemodel.xxx1"
      },
      {
        "inferenceKey": "model2",
        "modelId": "ocid.datasciencemodel.xxx2"
      },
      {
        "inferenceKey": "model3",
        "modelId": "ocid.datasciencemodel.xxx3"
      }
    ]
  }
}
```

> **Note:**  
> For **BYOC**, Model Deployment enforces a **contract** that containers must follow:
> - Must expose a web server.
> - Must include all runtime dependencies needed to load and run the ML model binaries.

## Dependency Management for Heterogeneous Model Group

> **Note:** This section is applicable only when using the **NVIDIA Triton Inference Server** for Heterogeneous deployments.

### Overview

Triton supports multiple ML frameworks and serves them through corresponding backends.

Triton loads models from one or more **model repositories**, each containing framework-specific models and configuration files.

### Natively Supported Backends

For native backends (e.g., ONNX, TF, PT), models must be organized as per **Triton model repository format**.

#### Sample ONNX Model Directory Structure

```
model_repository/
└── onnx_model/
    ├── 1/
    │   └── model.onnx
    └── config.pbtxt
```

#### Sample `config.pbtxt`

```text
name: "onnx_model"
platform: "onnxruntime_onnx"
input [
  {
    name: "input_tensor"
    data_type: TYPE_FP32
    dims: [ -1, 3, 224, 224 ]
  }
]
output [
  {
    name: "output_tensor"
    data_type: TYPE_FP32
    dims: [ -1, 1000 ]
  }
]
```

✅ No dependency conflicts are expected for natively supported models.

### Using Python Backend

For models that are not supported natively, Triton provides a **Python backend**.

#### Python Model Directory Structure

```
models/
└── add_sub/
    ├── 1/
    │   └── model.py
    └── config.pbtxt
```

#### If Python Version Differs (Custom Stub)

If the default Python version is insufficient, compile a **custom Python backend stub**.

```
models/
└── model_a/
    ├── 1/
    │   └── model.py
    ├── config.pbtxt
    └── triton_python_backend_stub
```

### Models with Custom Execution Environments

Use **Conda-Pack** to bundle all Python dependencies and isolate them per model.

#### Sample Structure with Conda-Pack

```
models/
└── model_a/
    ├── 1/
    │   └── model.py
    ├── config.pbtxt
    ├── env/
    │   └── model_a_env.tar.gz
    └── triton_python_backend_stub
```

#### Add This to `config.pbtxt` for Custom Environment

```text
name: "model_a"
backend: "python"

parameters: {
  key: "EXECUTION_ENV_PATH",
  value: {string_value: "$$TRITON_MODEL_DIRECTORY/env/model_a_env.tar.gz"}
}
```
