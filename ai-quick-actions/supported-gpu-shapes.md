

# Supported GPU Shapes

Below is the list of supported GPU shapes for model deployment and compute workloads. For detailed pricing, availability, and region support, refer to the [OCI GPU documentation](https://docs.oracle.com/en-us/iaas/Content/Compute/References/computeshapes.htm).

## Notes

* **BM (Bare Metal)** shapes offer full GPU hardware access, ideal for training and high-performance workloads.
* **VM (Virtual Machine)** shapes are suitable for cost-effective and scalable inference tasks.
* **MI300X and H200** shapes are the latest high-memory options designed for large language model (LLM) training and inference.


| Shape Name       | GPU Count | GPU Memory (GB) | GPU Type |
| ---------------- | --------- | --------------- | -------- |
| BM.GPU.A10.4     | 4         | 96              | A10      |
| BM.GPU.A100-V2.8 | 8         | 640             | A100     |
| BM.GPU.B4.8      | 8         | 320             | A100     |
| BM.GPU.H100.8    | 8         | 640             | H100     |
| BM.GPU.H200.8    | 8         | 1128            | H200     |
| BM.GPU.L40S-NC.4 | 4         | 192             | L40S     |
| BM.GPU.L40S.4    | 4         | 192             | L40S     |
| BM.GPU.MI300X.8  | 8         | 1536            | MI300X   |
| BM.GPU2.2        | 2         | 32              | P100     |
| BM.GPU3.8        | 8         | 128             | V100     |
| BM.GPU4.8        | 8         | 320             | A100     |
| VM.GPU.A10.1     | 1         | 24              | A10      |
| VM.GPU.A10.2     | 2         | 48              | A10      |
| VM.GPU.A10.4     | 4         | 96              | A10      |
| VM.GPU2.1        | 1         | 16              | P100     |
| VM.GPU3.1        | 1         | 16              | V100     |
| VM.GPU3.2        | 2         | 32              | V100     |
| VM.GPU3.4        | 4         | 64              | V100     |

