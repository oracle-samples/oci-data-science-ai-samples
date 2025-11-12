# AI Quick Actions Release Notes

## v2.0.0 (Nov 2025)
**Highlights:**
- **UI Enhancements:**
  - AI Quick Actions support for OpenAI Endpoint Model Deployment
    - Deploy models to multiple, configurable OpenAI endpoints—including support for streaming and advanced parameters.
- **Stacked Model Deployment**
  - AI Quick Actions introduce Stacked Model Deployment, enabling multiple fine-tuned variants to share the same base model deployment. This unified setup significantly improves GPU utilization compared to managing separate instances for each variant.
  For more details, refer to the corresponding [AI Quick Actions Stacked Deployment](https://github.com/oracle-samples/oci-data-science-ai-samples/blob/main/ai-quick-actions/stacked-deployment-tips.md).
- **Quantization Support for Models**
  - Use quantization to lower memory requirements, enabling large language model deployments on smaller, cost-effective compute shapes. For more details, see. [Using Quantization in AQUA](https://github.com/oracle-samples/oci-data-science-ai-samples/blob/main/ai-quick-actions/quantization-tips.md).
- **Llama 4 Fine-Tuning support**
  - Fine-tune Llama 4 models for greater customization and control to address your unique AI needs.
- **vLLM 0.11 and llama.cpp 0.3.16**  are now available, providing updated support for your AI model deployment needs.

To get this version of AI Quick Actions, deactivate and reactivate your notebook sessions.

---

## v1.0.8e (Released August 20, 2025)
**Highlights:**
- **Cached Model Upgrade – OpenAI Open Weight Models:**
  - Added cached support for OpenAI’s new open-weight models (gpt-oss-120b, gpt-oss-20b).
  - Models are available for deployment and fine-tuning without importing artifacts, supported in service-managed containers with the latest vLLM.
  - gpt-oss-120b: 117B parameters (5.1B active), optimized for production and high-reasoning.
  - gpt-oss-20b: 21B parameters (3.6B active), optimized for low-latency and specialized workloads.
  - Deliver strong performance on tool use, few-shot function calling, CoT reasoning, and HealthBench.

To get this version of AI Quick Actions, deactivate and reactivate your notebook sessions.

---

## v1.0.8d (Released August 4, 2025)
**Highlights:**
- **Model Deployment Enhancements:**
  - Added streaming endpoint integration for model deployments, enabling real-time inferencing with lower latency.
- **Cached Model Upgrades:**
  - Granite Speech 3.3 (Speech-to-Text): Upload audio (≤4 MB) in the Inference Playground to run speech-to-text with one click.
  - Granite Timeseries TTM R1: New model for advanced time series forecasting.
- **CLI Enhancements:**
  - Added policy verification tools to simplify validation of security and access policies.
- **Preview Models:**
  - Granite 4.0 (Text-to-Text): Preview model with improved NLP performance.

To get this version of AI Quick Actions, deactivate and reactivate your notebook sessions.

---

## v1.0.8c (Released July 24, 2025)
**Highlights:**
- **Platform Expansion:**
  - AI Quick Actions is now available in Government (Gov) and Oracle National Security Regions (ONSR), supporting compliance, security, and localized deployments.
- **Cached Model Upgrade:**
  - Added cached model support for Llama 3.2 and Llama 4, available for immediate deployment and fine-tuning without registration.

To get this version of AI Quick Actions, deactivate and reactivate your notebook sessions.

---

## v1.0.8b (Released July 21, 2025)
**Highlights:**
- **UI Enhancements:**
  - Bring Your Own Reservation (BYOR) Support:
    - Customers can now view and use existing GPU reservations directly in AI Quick Actions.
    - Workloads can be launched seamlessly without manual coordination or transfers.

To get this version of AI Quick Actions, deactivate and reactivate your notebook sessions.

---

## v1.0.8a (Released June 26, 2025)
**Highlights:**
- **Cached Model Upgrade – Granite 3 Models Support:**
  - Added support for IBM’s Granite 3 models as service cached models, available directly in the Model Explorer for deployment and fine-tuning.
  - Granite-3.3-2b-Instruct: 2B parameters, 128K context, tuned for reasoning and instruction following.
  - Granite-3.3-8b-Instruct / GGUF: 8B parameters, 128K context; GGUF variant supports CPU.
  - Granite-Vision-3.2-2b: Vision-language model for document understanding (tables, charts, diagrams, infographics).
  - Granite-Embedding-278m-multilingual: Embedding model for high-quality multilingual text representations.

To get this version of AI Quick Actions, deactivate and reactivate your notebook sessions.

---

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
