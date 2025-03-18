# Latest inference containers supported in AI Quick Actions

| Server                                                                                                          | Version     |Supported Formats|Supported Shapes| Supported Models/Architectures                                                                                                  |
|-----------------------------------------------------------------------------------------------------------------|-------------|-----------------|----------------|---------------------------------------------------------------------------------------------------------------------------------|
| [vLLM](https://github.com/vllm-project/vllm/releases/tag/v0.6.4.post1)                                          | 0.6.4.post1.1 |safe-tensors|A10, A100, H100| [v0.6.4.post1 supported models](https://docs.vllm.ai/en/v0.6.4.post1/models/supported_models.html)                   |
| [Text Generation Inference (TGI)](https://github.com/huggingface/text-generation-inference/releases/tag/v2.0.1) | 2.0.1.4     |safe-tensors|A10, A100, H100| [v2.0.1 supported models](https://github.com/huggingface/text-generation-inference/blob/v2.0.1/docs/source/supported_models.md) |
| [Llama-cpp](https://github.com/abetlen/llama-cpp-python/releases/tag/v0.3.2)                                   | 0.3.2.0    |gguf|Amphere ARM| [llama.cpp@fd5ea0f supported models](https://github.com/ggml-org/llama.cpp/tree/74d73dc85cc2057446bf63cc37ff649ae7cebd80)      |


<!-- 
The below content is hidden in the markdown, useful for updating the above table:

- Steps to find supported models list: 
1. vLLM
    - Visit the vLLM documentation page for supported models https://docs.vllm.ai/en/latest/models/supported_models.html
    - In the bottom right, switch to the required vLLM version. 

2. TGI
    - Visit the supported models page in TGI github repo https://github.com/huggingface/text-generation-inference/blob/main/docs/source/supported_models.md
    - Select the version tag on the left pane, for example v2.0.1. 
3. Llama-cpp-python
    - Visit the llama-cpp-python repo and select the version tag. For example: https://github.com/abetlen/llama-cpp-python/tree/v0.2.78/vendor
    - Click on the llama.cpp commit used by this version.
    - Scroll down in the readme page and find the section on Supported Models. Link to the section if a hyperlink is available, else link the markdown.
-->   
