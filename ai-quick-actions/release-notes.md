# AI Quick Actions Release Notes


## v1.0.7a (Released May 29, 2025)
**Highlights:**
- **UI Enhancements:**
  - Multi Model deployment support
    - Users can now deploy multiple LLM models on a single instance, improving GPU utilization and simplifying how models are managed and served. 
    - Inference requests are routed dynamically through LiteLLM, allowing users to pick models at runtime without redeploying.
    - Fully validated GPU allocations across models.

For more details, refer to the corresponding [AI Quick Actions MultiModel Deployment documentation](https://github.com/oracle-samples/oci-data-science-ai-samples/blob/main/ai-quick-actions/multimodel-deployment-tips.md).
To get this version of AI Quick Actions, deactivate and reactivate your notebook sessions.

---

## v1.0.7 (Released April 23, 2025)
**Highlights:**
- **UI Enhancements:**
  - We have made UI improvements based on customer feedback to enhance troubleshooting experience. 
    - User will be able to copy the error payload for faster resolution and sharing.
  - Improved Model registration , Deployment and Evaluation flow using metadata APIs
- **AQUA CLI Enhancements:**
  - Added support for creating deployments with multiple verified or cached LLM (text-generation) models using the AI Quick Actions CLI. For more details, refer to the corresponding [AI Quick Actions MultiModel Deployment documentation](https://github.com/oracle-samples/oci-data-science-ai-samples/blob/main/ai-quick-actions/multimodel-deployment-tips.md).

To get this version of AI Quick Actions, deactivate and reactivate your notebook sessions.

---

## v1.0.6d (Released February April 17, 2025)
**Highlights:**
- **Cached Model Upgrade:**
  - Introduced Phi 4 and Phi 3.5 as a service cached model.
- **Container Enhancements:**
  - Upgraded managed containers are now running [vLLM 0.8.3](https://github.com/vllm-project/vllm/releases/tag/v0.8.3). This version of vLLM supports the newly released Meta's Llama 4 models. 
- **UI Enhancements:**
  - We have made UI improvements based on customer feedback and to better help customers troubleshoot, including link to the AI Quick Actions [Troubleshooting page](https://github.com/oracle-samples/oci-data-science-ai-samples/blob/main/ai-quick-actions/troubleshooting-tips.md). 

To get this version of AI Quick Actions, deactivate and reactivate your notebook sessions.

---

## v1.0.6b (Released February 28, 2025)
**Highlights:**
- **Cached Model Upgrade:**
  - Introduced Llama 3.1 as a service cached model.
- **Container Enhancements:**
  - Upgraded managed containers are now running [vLLM 0.7.1](https://github.com/vllm-project/vllm/releases/tag/v0.7.1) and [llama.cpp 0.3.2](https://github.com/abetlen/llama-cpp-python/releases/tag/v0.3.2).

To get this version of AI Quick Actions, deactivate and reactivate your notebook sessions.

For more details, refer to the corresponding [Oracle release notes](https://docs.oracle.com/en-us/iaas/releasenotes/data-science/ai-quick-actions-106-b.htm).

---

## v1.0.6a (Released January 30, 2025)
**Enhancements and Features:**

- Expanded multiple inference endpoint support
  - You can now use the chat completion endpoint in the inference playground.
  - You can select Copy payload in the inference playground to get the model endpoint and get code sample to invoke the model with the CLI that corresponds to the completion or chat completion inference format.
- Exclusion of files during model registration
  - You have the option to exclude files based on file format during the model registration process. This is helpful when you want to bring in a model from Hugging Face to AI Quick Actions and want to exclude certain files from being downloaded such as .txt and .pdf files.
- Addition of copy model ocid feature in model details page
  - After registering the model, you can find and copy the model ocid in the model details page without navigating to the Console to find the model ocid.
- Model details actions button UI changes
- Tool calling support
  - AI Quick Actions now has a version of vllm container that supports tool calling capabilities. Tool calling lets a model invoke external functions during inference, enhancing its ability to provide context-specific answers.

To get this version of AI Quick Actions, deactivate and reactivate your notebook sessions.

For more details, refer to the corresponding [Oracle release notes](https://docs.oracle.com/en-us/iaas/releasenotes/data-science/aqua-106-a.htm).

---

## v1.0.5 (Released January 30, 2025)

**Enhancements and Features:**
- Expanded multiple inference endpoint support
  - You can now use the chat completion endpoint in the inference playground.
  - You can select Copy payload in the inference playground to get the model endpoint and get code sample to invoke the model with the CLI that corresponds to the completion or chat completion inference format.
- Exclusion of files during model registration
  - You have the option to exclude files based on file format during the model registration process. This is helpful when you want to bring in a model from Hugging Face to AI Quick Actions and want to exclude certain files from being downloaded such as .txt and .pdf files.
- Addition of copy model ocid feature in model details page
  - After registering the model, you can find and copy the model ocid in the model details page without navigating to the Console to find the model ocid.
- Model details actions button UI changes
- Tool calling support
  - AI Quick Actions now has a version of vllm container that supports tool calling capabilities. Tool calling lets a model invoke external functions during inference, enhancing its ability to provide context-specific answers.

To get this version of AI Quick Actions, deactivate and reactivate your notebook sessions.

For more details, refer to the corresponding [Oracle release notes](https://docs.oracle.com/iaas/releasenotes/data-science/aqua-105-fast-follow.htm).

---

## v1.0.4 (Released October 04, 2024)

**Enhancements and Features:**
- With AI Quick Actions v 1.0.4, Data Science now supports the following evaluation metrics:
  - perplexity score
  - text readability
- The following ready to register models are now supported and are available in all regions bar in the EU:
  - meta-llama/Meta-Llama-3.1-8B
  - meta-llama/Meta-Llama-3.1-8B-Instruct
  - meta-llama/Meta-Llama-3.1-70B
  - meta-llama/Meta-Llama-3.1-70B-Instruct
  - meta-llama/Meta-Llama-3.1-405B-Instruct-FP8
  - meta-llama/Meta-Llama-3.1-405B-FP8
  - meta-llama/Llama-3.2-1B
  - meta-llama/Llama-3.2-1B-Instruct
  - meta-llama/Llama-3.2-3B
  - meta-llama/Llama-3.2-3B-Instruct
  - meta-llama/Llama-3.2-11B-Vision
  - meta-llama/Llama-3.2-90B-Vision
  - meta-llama/Llama-3.2-11B-Vision-Instruct
  - meta-llama/Llama-3.2-90B-Vision-Instruct
To get this version of AI Quick Actions, deactivate and reactivate your notebook sessions.

For more details, refer to the corresponding [Oracle release notes](https://docs.oracle.com/iaas/releasenotes/data-science/aqua-104.htm).

---

## v1.0.3 (Released August 23, 2024)

**Enhancements and Features:**
- Arm compute shapes
- The llama.cpp container
- Importing models from Hugging Face.


For more details, refer to the corresponding [Oracle release notes](https://docs.oracle.com/iaas/releasenotes/data-science/aqua-103.htm).

---
