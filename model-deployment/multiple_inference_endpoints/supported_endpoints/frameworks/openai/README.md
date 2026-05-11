# OpenAI — Supported Endpoints

When a Model Deployment is created with `predict_api_specification = "openai"`, the endpoints listed below are automatically exposed by the deployment.

This list is the **source of truth** for the OpenAI framework on OCI Data Science Model Deployment. Anything not in this list is not guaranteed to be routed by the platform for the OpenAI specification.

> The actual behavior of each endpoint (request schema, response schema, streaming, etc.) is determined by the inference container you deploy (for example vLLM, TGI, or an OpenAI-compatible server). The platform's responsibility is to **route** these paths to your container.

## Supported endpoints

```text
/v1/models
/v1/completions
/v1/chat/completions
/v1/edits
/v1/images/generations
/v1/images/edits
/v1/images/variations
/v1/embeddings
/v1/audio/transcriptions
/v1/audio/translations
/v1/files
/v1/fine-tunes
/v1/moderations
/v1/responses
/tokenize
/detokenize
/version
/start_profile
/stop_profile
/v1/load_lora_adapter
/v1/unload_lora_adapter
/metrics
/chat_tokenize
/generate
/generate_stream
/info
/invocations
/v1/responses/{}
/v1/responses/{}/cancel
/v1/responses/{}/input_items
/v1/messages
```

## Related samples

* [Create a model deployment with MIE (SDK)](../../../samples/create_model_deployment/sdk/create_mie_md.py)
* [Create a model deployment with MIE (REST JSON + script)](../../../samples/create_model_deployment/api_payload/)
* [Update a model deployment with MIE (SDK)](../../../samples/update_model_deployment/sdk/update_mie_md.py)
* [Update a model deployment with MIE (REST JSON + script)](../../../samples/update_model_deployment/api_payload/)
* [Inference (non-streaming)](../../../samples/inference/non_streaming/inference_mie.py)
* [Inference (streaming)](../../../samples/inference/streaming/inference_mie_streaming.py)
* [OpenAI SDK auth samples](../../../openai_sdk_auth/README.md)
