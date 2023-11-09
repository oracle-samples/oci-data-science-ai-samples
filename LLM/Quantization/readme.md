# Quantizing Llama 2 70B
This sample provides a step-by-step walkthrough on quantizing a Llama 2 70B model to 4 bit weights, so it can fit 2xA10 GPUs.
The sample uses GPTQ in HuggingFace transformer to reduce the weights parameters to 4 bit so the model weighs about 35GB in memory.

## Prerequisites
* [Create an object storage bucket](https://github.com/oracle-samples/oci-data-science-ai-samples/tree/main/distributed_training#2-object-storage) - to save the quantized model to the mdoel catalog
* [Set the policies](https://github.com/oracle-samples/oci-data-science-ai-samples/tree/main/distributed_training#3-oci-policies) - to allow the OCI Data Science Service resources to access object storage buckets, networking and others
* [Notebook session](https://docs.oracle.com/en-us/iaas/data-science/using/manage-notebook-sessions.htm) - to run this sample. Use the **VM.GPU.A10.2** shape for the notebook session.
* [Access token from HuggingFace](https://huggingface.co/docs/hub/security-tokens) to download Llama2 model. The pre-trained model can be obtained from [Meta](https://ai.meta.com/resources/models-and-libraries/llama-downloads/) or [HuggingFace](https://huggingface.co/models?sort=trending&search=meta-llama%2Fllama-2). In this example, we will use the [HuggingFace access token](https://huggingface.co/docs/hub/security-tokens) to download the pre-trained model from HuggingFace (by setting the __HUGGING_FACE_HUB_TOKEN__ environment variable).
* Log in to HuggingFace with the auth token:
  * Open a terminal window in the notebook session
  * enter the command line: huggingface-cli login
  * paste the auth token
  * see more information [here](https://huggingface.co/docs/huggingface_hub/quick-start#login)
* Install required python libraries (from terminal window):
```python
pip install "transformers[sentencepiece]==4.32.1" "optimum==1.12.0" "auto-gptq==0.4.2" "accelerate==0.22.0" "safetensors>=0.3.1" --upgrade
```

## Load the full model
We can load the full model using the device_map="auto" argument. This will use CPU to store the weights that cannot be loaded into the GPUs.

```python
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
 
model_id = "meta-llama/Llama-2-70b-hf"
 
tokenizer = AutoTokenizer.from_pretrained(model_id, use_fast=False)
 
model_full = AutoModelForCausalLM.from_pretrained(
    model_id,
    low_cpu_mem_usage=True,
    torch_dtype=torch.float16,
    device_map="auto",
)
```

By looking at the device map, we can see many layers are loaded into the CPU memory.
```python
model_full.hf_device_map
```

<details>
<summary>Full 70B model device map on A10.2</summary>

{'model.embed_tokens': 0,
 'model.layers.0': 1,
 'model.layers.1': 1,
 'model.layers.2': 1,
 'model.layers.3': 1,
 'model.layers.4': 1,
 'model.layers.5': 'cpu',
 'model.layers.6': 'cpu',
 'model.layers.7': 'cpu',
 'model.layers.8': 'cpu',
 'model.layers.9': 'cpu',
 'model.layers.10': 'cpu',
 'model.layers.11': 'cpu',
 'model.layers.12': 'cpu',
 'model.layers.13': 'cpu',
 'model.layers.14': 'cpu',
 'model.layers.15': 'cpu',
 'model.layers.16': 'cpu',
 'model.layers.17': 'cpu',
 'model.layers.18': 'cpu',
 'model.layers.19': 'cpu',
 'model.layers.20': 'cpu',
 'model.layers.21': 'cpu',
 'model.layers.22': 'cpu',
 'model.layers.23': 'cpu',
 'model.layers.24': 'cpu',
 'model.layers.25': 'cpu',
 'model.layers.26': 'cpu',
 'model.layers.27': 'cpu',
 'model.layers.28': 'cpu',
 'model.layers.29': 'cpu',
 'model.layers.30': 'cpu',
 'model.layers.31': 'cpu',
 'model.layers.32': 'cpu',
 'model.layers.33': 'cpu',
 'model.layers.34': 'cpu',
 'model.layers.35': 'cpu',
 'model.layers.36': 'cpu',
 'model.layers.37': 'cpu',
 'model.layers.38': 'cpu',
 'model.layers.39': 'cpu',
 'model.layers.40': 'cpu',
 'model.layers.41': 'cpu',
 'model.layers.42': 'cpu',
 'model.layers.43': 'cpu',
 'model.layers.44': 'cpu',
 'model.layers.45': 'cpu',
 'model.layers.46': 'cpu',
 'model.layers.47': 'cpu',
 'model.layers.48': 'cpu',
 'model.layers.49': 'cpu',
 'model.layers.50': 'cpu',
 'model.layers.51': 'cpu',
 'model.layers.52': 'cpu',
 'model.layers.53': 'cpu',
 'model.layers.54': 'cpu',
 'model.layers.55': 'cpu',
 'model.layers.56': 'cpu',
 'model.layers.57': 'cpu',
 'model.layers.58': 'cpu',
 'model.layers.59': 'cpu',
 'model.layers.60': 'cpu',
 'model.layers.61': 'cpu',
 'model.layers.62': 'cpu',
 'model.layers.63': 'cpu',
 'model.layers.64': 'cpu',
 'model.layers.65': 'cpu',
 'model.layers.66': 'cpu',
 'model.layers.67': 'cpu',
 'model.layers.68': 'cpu',
 'model.layers.69': 'cpu',
 'model.layers.70': 'cpu',
 'model.layers.71': 'cpu',
 'model.layers.72': 'cpu',
 'model.layers.73': 'cpu',
 'model.layers.74': 'cpu',
 'model.layers.75': 'cpu',
 'model.layers.76': 'cpu',
 'model.layers.77': 'cpu',
 'model.layers.78': 'cpu',
 'model.layers.79': 'cpu',
 'model.norm': 'cpu',
 'lm_head': 'cpu'}

</details>

## Quantize the model
It is possible to quantize the model on the A10.2 shapes. However, the max sequence length is limited due to the GPU RAM available.
Quantization requires a dataset to calibrate the quantized model. In this example we use the 'wikitext2' dataset.

We need to specify the maximum memory for the GPUs to load the model as we need to keep some extra memory for the quantization. Here we are specifying max_memory of 5GB for each GPU when loading the model.
Due to the size of the model and the limited memory on A10, for the quantization, we need to limit the maximum sequence length that the model can take (model_seqlen) to 128. You may increase this number by reducing the max_memory used by each CPU when loading the model.
We also need to set max_split_size_mb for PyTorch to reduce fragmentation.

The following parameters have been found to work when quantizing on A10.2:
max_split_size_mb = 512
max_memory = 5GB (for each GPU)
model_seqlen = 128

```python
import os
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, GPTQConfig
 
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "max_split_size_mb:512"
 
model_id = "meta-llama/Llama-2-70b-hf"
dataset_id = "wikitext2"
 
tokenizer = AutoTokenizer.from_pretrained(model_id, use_fast=False)
gptq_config = GPTQConfig(bits=4, dataset=dataset_id, tokenizer=tokenizer, model_seqlen=128)

model_quantized = AutoModelForCausalLM.from_pretrained(
    model_id,
    torch_dtype=torch.float16,
    device_map="auto",
    max_memory={0: "5GB", 1: "5GB", "cpu": "400GB"},
    quantization_config=gptq_config,
)
```

The process will show the progress over the 80 layers. It will take about 1 hour with the wikitext2 dataset.

Note that we cannot run inference on this particular "quantized model" as some "blocks" are loaded across multiple devices. For inferencing, we need to save the model and load it back.

Save the quantized model and the tokenizer:
```python
save_folder = "Llama-2-70b-hf-quantized"
model_quantized.save_pretrained(save_folder)
tokenizer.save_pretrained(save_folder)
```

Since the model was partially offloaded it set disable_exllama to True to avoid an error. For inference and production load we want to leverage the exllama kernels. Therefore we need to change the config.json:
Edit the config.json file, find the key 'disable_exllama' and set it to 'False'.

## Working with the quantized model
Now that the model is saved to the disk, we can see that its size is about 34.1GB. That aligns with our calculations, and can fit 2xA10 GPUs, which can handle up to 48GB in memory.

We can load the quantized model back without the max_memory limit:
```python
tokenizer_q = AutoTokenizer.from_pretrained(save_folder)
model_quantized = AutoModelForCausalLM.from_pretrained(
    save_folder,
    device_map="auto",
)
```

By checking the device map, we see the entire model is loaded into GPUs:
<details>
<summary>Quantized model device map on A10.2</summary>

{'model.embed_tokens': 0,
 'model.layers.0': 0,
 'model.layers.1': 0,
 'model.layers.2': 0,
 'model.layers.3': 0,
 'model.layers.4': 0,
 'model.layers.5': 0,
 'model.layers.6': 0,
 'model.layers.7': 0,
 'model.layers.8': 0,
 'model.layers.9': 0,
 'model.layers.10': 0,
 'model.layers.11': 0,
 'model.layers.12': 0,
 'model.layers.13': 0,
 'model.layers.14': 0,
 'model.layers.15': 0,
 'model.layers.16': 0,
 'model.layers.17': 0,
 'model.layers.18': 0,
 'model.layers.19': 0,
 'model.layers.20': 0,
 'model.layers.21': 0,
 'model.layers.22': 0,
 'model.layers.23': 0,
 'model.layers.24': 0,
 'model.layers.25': 0,
 'model.layers.26': 0,
 'model.layers.27': 0,
 'model.layers.28': 0,
 'model.layers.29': 0,
 'model.layers.30': 0,
 'model.layers.31': 0,
 'model.layers.32': 0,
 'model.layers.33': 0,
 'model.layers.34': 0,
 'model.layers.35': 0,
 'model.layers.36': 0,
 'model.layers.37': 0,
 'model.layers.38': 1,
 'model.layers.39': 1,
 'model.layers.40': 1,
 'model.layers.41': 1,
 'model.layers.42': 1,
 'model.layers.43': 1,
 'model.layers.44': 1,
 'model.layers.45': 1,
 'model.layers.46': 1,
 'model.layers.47': 1,
 'model.layers.48': 1,
 'model.layers.49': 1,
 'model.layers.50': 1,
 'model.layers.51': 1,
 'model.layers.52': 1,
 'model.layers.53': 1,
 'model.layers.54': 1,
 'model.layers.55': 1,
 'model.layers.56': 1,
 'model.layers.57': 1,
 'model.layers.58': 1,
 'model.layers.59': 1,
 'model.layers.60': 1,
 'model.layers.61': 1,
 'model.layers.62': 1,
 'model.layers.63': 1,
 'model.layers.64': 1,
 'model.layers.65': 1,
 'model.layers.66': 1,
 'model.layers.67': 1,
 'model.layers.68': 1,
 'model.layers.69': 1,
 'model.layers.70': 1,
 'model.layers.71': 1,
 'model.layers.72': 1,
 'model.layers.73': 1,
 'model.layers.74': 1,
 'model.layers.75': 1,
 'model.layers.76': 1,
 'model.layers.77': 1,
 'model.layers.78': 1,
 'model.layers.79': 1,
 'model.norm': 1,
 'lm_head': 1}

</details>

## Testing the model
We can use the Huggingface pipeline to test the model inference.

```python
import time
from transformers import pipeline
 
def generate(prompt, model, tokenizer, **kwargs):
    """Creates a text generation pipeline, generate the completion and track the time used for the generation."""
    generator = pipeline("text-generation", model=model, tokenizer=tokenizer, max_new_tokens=256, return_full_text=False)
     
    # warm up
    generator("How are you?")
    generator("Oracle is a great company.")
     
    time_started = time.time()
    completion = generator(prompt)[0]['generated_text']
    seconds_used = time.time() - time_started
    print(completion)
    num_tokens = len(completion.split())
    latency = seconds_used*1000 / num_tokens
    token_per_sec = len(generator.tokenizer(completion)["input_ids"]) / seconds_used
    print(f"******\nTotal time: {seconds_used:.3f} \nNumber of tokens: {num_tokens} \nseconds \nThroughput: {token_per_sec:.2f} Tokens/sec \nLatency: {latency:.2f} ms/token")
```

Test the quantized model:
generate("What's AI?", model_quantized, tokenizer_q)

Output:
The AI 101 series is a collection of articles that will introduce you to the basics of artificial intelligence (AI). In this first article, we're going to talk about the history of AI, and how it has evolved over the years.
The first AI system was created in the 1950s, and it was called the Logic Theorist. This system was able to solve mathematical problems using a set of rules. The Logic Theorist was followed by other AI systems, such as the General Problem Solver and the Game of Checkers.
In the 1960s, AI researchers began to focus on developing systems that could understand natural language. This led to the development of the first chatbot, named ELIZA. ELIZA was able to hold a conversation with a human user by responding to their questions with pre-programmed responses.
In the 1970s, AI researchers began to focus on developing systems that could learn from data. This led to the development of the first expert system, named MYCIN. MYCIN was able to diagnose diseases by analyzing data from medical records.
******
Time used: 28.659 seconds

Number of tokens: 176 

Throughput: 9.00 Tokens/sec 

Latency: 111.11 ms/token

