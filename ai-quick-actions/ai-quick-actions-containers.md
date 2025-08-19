# Latest inference containers supported in AI Quick Actions

| Server                                                                                                          | Version     |Supported Formats|Supported Shapes| Supported Models/Architectures                                                                                                  |
|-----------------------------------------------------------------------------------------------------------------|-------------|-----------------|----------------|---------------------------------------------------------------------------------------------------------------------------------|
| [vLLM](https://github.com/vllm-project/vllm/releases/tag/v0.9.1)                                                | 0.9.1       |safe-tensors|A10, A100, H100| [v0.9.1 supported models](https://docs.vllm.ai/en/v0.9.1/models/supported_models.html)                                          |
| [Text Generation Inference (TGI)](https://github.com/huggingface/text-generation-inference/releases/tag/v3.2.1) | 3.2.1     |safe-tensors|A10, A100, H100| [v3.2.1 supported models](https://github.com/huggingface/text-generation-inference/blob/v3.2.1/docs/source/supported_models.md) |
| [Llama-cpp](https://github.com/abetlen/llama-cpp-python/releases/tag/v0.3.7)                                    | 0.3.7       |gguf|Amphere ARM| [v0.3.7 supported models](https://github.com/abetlen/llama-cpp-python/tree/v0.3.7)                                              |


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
