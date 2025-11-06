# Model Deployment

Table of Contents:

- [Home](README.md)
- [Policies](policies/README.md)
- [CLI](cli-tips.md)
- [Model Fine Tuning](fine-tuning-tips.md)
- [Model Evaluation](evaluation-tips.md)
- [Model Registration](register-tips.md)
- [Multi Modal Inferencing](multimodal-models-tips.md)
- [Private_Endpoints](model-deployment-private-endpoint-tips.md)
- [Tool Calling](model-deployment-tool-calling-tips.md)

## Introduction to Model Inference and Serving

The Data Science server has prebuilt service containers that make deploying and serving a large
language model very easy. Either one of [vLLM](https://github.com/vllm-project/vllm) (a high-throughput and memory-efficient inference and serving
engine for LLMs) or [TGI](https://github.com/huggingface/text-generation-inference) (a high-performance text generation server for the popular open-source LLMs) is used in the service container to host the model, the end point created
supports the OpenAI API protocol.  This allows the model deployment to be used as a drop-in
replacement for applications using OpenAI API. Model deployments are a managed resource in
the OCI Data Science service. For more details about Model Deployment and managing it through
the OCI console please see the [OCI docs](https://docs.oracle.com/en-us/iaas/data-science/using/model-dep-about.htm).


### Prerequisites

1. Ensure that the necessary [policies](policies/README.md) are enacted.
2. Create an OCI Object Storage Bucket with Object Versioning.

![Bucket w/ Object Versioning](web_assets/object-versioning.png)

### Deploying an LLM

After picking a model from the model explorer, if the "Deploy Model" is enabled you can use this
form to quickly deploy the model:

![Deploy Model](web_assets/deploy-model.png)

### Compute Shape

The compute shape selection is critical, the list available is selected to be suitable for the
chosen model.

- VM.GPU.A10.1 has 24GB of GPU memory and 240GB of CPU memory. The limiting factor is usually the
GPU memory which needs to be big enough to hold the model.
- VM.GPU.A10.2 has 48GB GPU memory
- BM.GPU.A10.4 has 96GB GPU memory and runs on a bare metal machine, rather than a VM.

For a full list of shapes and their definitions see the [compute shape docs](https://docs.oracle.com/en-us/iaas/Content/Compute/References/computeshapes.htm)

The relationship between model parameter size and GPU memory is roughly 2x parameter count in GB, so for example a model that has 7B parameters will need a minimum of 14 GB for inference. At runtime the
memory is used for both holding the weights, along with the concurrent contexts for the user's requests.

### Advanced Options

You may click on the "Show Advanced Options" to configure options for "inference container" and "inference mode".

![Advanced Options](web_assets/deploy-model-advanced-options.png)

### Inference Container Configuration

The service allows for model deployment configuration to be overridden when creating a model deployment. Depending on
the type of inference container used for deployment, i.e. vLLM or TGI, the parameters vary and need to be passed with the format
`(--param-name, param-value)`.

For more details, please visit [vLLM](https://docs.vllm.ai/en/latest/serving/openai_compatible_server.html#command-line-arguments-for-the-server) or
[TGI](https://huggingface.co/docs/text-generation-inference/en/basic_tutorials/launcher) documentation to know more about the parameters accepted by the respective containers.

### Inference Mode

The "inference mode" allows you to choose between the default completion endpoint(`/v1/completions`) and the chat endpoint (`/v1/chat/completions`).
* The default completion endpoint is designed for text completion tasks. It’s suitable for generating text based on a given prompt.
* The chat endpoint is tailored for chatbot-like interactions. It allows for more dynamic and interactive conversations by using a list of messages with roles (system, user, assistant). This is ideal for applications requiring back-and-forth dialogue, maintaining context over multiple turns. It is recommended that you deploy chat models (e.g. `meta-llama/Llama-3.1-8B-Instruct`) using the chat endpoint.


### Test Your Model

Once deployed, the model will spin up and become available after some time, then you're able to try out the model
from the deployments tab using the test model, or programmatically.

![Try Model](web_assets/try-model.png)


## Inferencing Model

### Using oci-cli

```bash
oci raw-request --http-method POST --target-uri <model_deployment_url>/predict --request-body '{
        "model": "odsc-llm",
        "prompt":"what are activation functions?",
        "max_tokens":250,
        "temperature": 0.7,
        "top_p":0.8,
    }' --auth <auth_method>
```

Note: Currently `oci-cli` does not support streaming response, use Python or Java SDK instead.

#### Request body for /v1/completions VS /v1/chat/completions

For /v1/completion endpoints, use the "prompt" key.
```
body = {
    "model": "odsc-llm", # this is a constant
    "prompt": "what are activation functions?",
    "max_tokens": 250,
    "temperature": 0.7,
    "top_p": 0.8,
}
```

For v1/chat/completions, use the "messages" key and a list of JSONs.
```
body = {
    "model": "odsc-llm", # this is a constant
    "messages": [{"content" : "what model are you?", "role":"user"}],
    "max_tokens": 250,
    "temperature": 0.7,
    "top_p": 0.8,
}
```
#### Using Python SDK (without streaming)

- note that the following request body is for the **/v1/completions** endpoint
- See **/v1/chat/completions** request body [here](#request-body-for-/v1/completions-vs-/v1/chat/completions)

```python
# The OCI SDK must be installed for this example to function properly.
# Installation instructions can be found here: https://docs.oracle.com/en-us/iaas/Content/API/SDKDocs/pythonsdk.htm

import requests
import oci
from oci.signer import Signer
from oci.config import from_file

config = from_file('~/.oci/config')
auth = Signer(
    tenancy=config['tenancy'],
    user=config['user'],
    fingerprint=config['fingerprint'],
    private_key_file_location=config['key_file'],
    pass_phrase=config['pass_phrase']
)

# For security token based authentication
# token_file = config['security_token_file']
# token = None
# with open(token_file, 'r') as f:
#     token = f.read()
# private_key = oci.signer.load_private_key_from_file(config['key_file'])
# auth = oci.auth.signers.SecurityTokenSigner(token, private_key)

endpoint = "https://modeldeployment.us-ashburn-1.oci.oc-test.com/ocid1.datasciencemodeldeployment.oc1.iad.xxxxxxxxx/predict"
body = {
    "model": "odsc-llm", # this is a constant
    "prompt": "what are activation functions?",
    "max_tokens": 250,
    "temperature": 0.7,
    "top_p": 0.8,
}

res = requests.post(endpoint, json=body, auth=auth, headers={}).json()

print(res)
```

### Using Python SDK (with streaming)

**Note:** For streaming, a different endpoint should be used: `/predictWithResponseStream`. You can find more details in the official documentation [here](https://docs.oracle.com/en-us/iaas/Content/data-science/using/model-dep-invoke.htm).

To consume Server-Sent Events (SSE) from this endpoint, you’ll need to install the [`sseclient-py`](https://pypi.org/project/sseclient-py/) package:

```bash
pip install sseclient-py
```

- note that the following request body is for the **/v1/completions** endpoint
- See **/v1/chat/completions** request body [here](#request-body-for-/v1/completions-vs-/v1/chat/completions)
```python
# The OCI SDK must be installed for this example to function properly.
# Installation instructions can be found here: https://docs.oracle.com/en-us/iaas/Content/API/SDKDocs/pythonsdk.htm

import requests
import oci
from oci.signer import Signer
from oci.config import from_file
import sseclient # pip install sseclient-py

config = from_file('~/.oci/config')
auth = Signer(
    tenancy=config['tenancy'],
    user=config['user'],
    fingerprint=config['fingerprint'],
    private_key_file_location=config['key_file'],
    pass_phrase=config['pass_phrase']
)

# For security token based authentication
# token_file = config['security_token_file']
# token = None
# with open(token_file, 'r') as f:
#     token = f.read()
# private_key = oci.signer.load_private_key_from_file(config['key_file'])
# auth = oci.auth.signers.SecurityTokenSigner(token, private_key)

endpoint = "https://modeldeployment.us-ashburn-1.oci.oc-test.com/ocid1.datasciencemodeldeployment.oc1.iad.xxxxxxxxx/predictWithResponseStream"
body = {
    "model": "odsc-llm", # this is a constant
    "prompt": "what are activation functions?",
    "max_tokens": 250,
    "temperature": 0.7,
    "top_p": 0.8,
    "stream": True,
}

headers={'Content-Type':'application/json', 'Accept': 'text/event-stream'}
response = requests.post(endpoint, json=body, auth=auth, stream=True, headers=headers)

print(response.headers)

client = sseclient.SSEClient(response)
for event in client.events():
    print(event.data)

# Alternatively, we can use the below code to print the response.
# for line in response.iter_lines():
#    if line:
#        print(line)
```

### Using Python SDK for v1/chat/completions endpoint

To access the model deployed with `v1/chat/completions` endpoint for inference, update the body and replace `prompt` field
with `messages`.

```python
...
body = {
    "model": "odsc-llm", # this is a constant
    "messages":[{"role":"user","content":[{"type":"text","text":"Who wrote the book Harry Potter?"}]}],
    "max_tokens": 250,
    "temperature": 0.7,
    "top_p": 0.8,
}
...
```
For multi-modal inference, refer the page [Multimodal Model Tips](multimodal-models-tips.md) for an example to access `v1/chat/completions` endpoint.

### Using Java (with streaming)

**Note:** For streaming, a different endpoint should be used: `/predictWithResponseStream`. You can find more details in the official documentation [here](https://docs.oracle.com/en-us/iaas/Content/data-science/using/model-dep-invoke.htm).

```java
/**
 * The OCI SDK must be installed for this example to function properly.
 * Installation instructions can be found here: https://docs.oracle.com/en-us/iaas/Content/API/SDKDocs/javasdk.htm
 */
package org.example;

import com.oracle.bmc.auth.AuthenticationDetailsProvider;
import com.oracle.bmc.auth.SessionTokenAuthenticationDetailsProvider;
import com.oracle.bmc.http.ClientConfigurator;
import com.oracle.bmc.http.Priorities;
import com.oracle.bmc.http.client.HttpClient;
import com.oracle.bmc.http.client.HttpClientBuilder;
import com.oracle.bmc.http.client.HttpRequest;
import com.oracle.bmc.http.client.HttpResponse;
import com.oracle.bmc.http.client.Method;
import com.oracle.bmc.http.client.jersey.JerseyHttpProvider;
import com.oracle.bmc.http.client.jersey.sse.SseSupport;
import com.oracle.bmc.http.internal.ParamEncoder;
import com.oracle.bmc.http.signing.RequestSigningFilter;

import javax.ws.rs.core.MediaType;
import java.io.BufferedReader;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.net.URI;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.function.Function;

public class RestExample {

    public static void main(String[] args) throws Exception {
        String configurationFilePath = "~/.oci/config";
        String profile = "DEFAULT";

        // Pre-Requirement: Allow setting of restricted headers. This is required to allow the SigningFilter
        // to set the host header that gets computed during signing of the request.
        System.setProperty("sun.net.http.allowRestrictedHeaders", "true");

        final AuthenticationDetailsProvider provider =
                new SessionTokenAuthenticationDetailsProvider(configurationFilePath, profile);

        // 1) Create a request signing filter instance using SessionTokenAuth Provider.
        RequestSigningFilter requestSigningFilter = RequestSigningFilter.fromAuthProvider(
                provider);

      //  1) Alternatively, RequestSigningFilter can be created from a config file.
      //  RequestSigningFilter requestSigningFilter = RequestSigningFilter.fromConfigFile(configurationFilePath, profile);

        // 2) Create a Jersey client and register the request signing filter.
        // Refer to this page https://docs.oracle.com/en-us/iaas/Content/API/SDKDocs/javasdkexamples.htm for information regarding the compatibility of the HTTP client(s) with OCI SDK version.

        HttpClientBuilder builder = JerseyHttpProvider.getInstance()
                .newBuilder()
                .registerRequestInterceptor(Priorities.AUTHENTICATION, requestSigningFilter)
                .baseUri(
                        URI.create(
                                "${modelDeployment.modelDeploymentUrl}/")
                                + ParamEncoder.encodePathParam("predictWithResponseStream"));
        // 3) Create a request and set the expected type header.

        String jsonPayload = "{}";  // Add payload here with respect to your model example shown in next line:

        // 4) Setup Streaming request
        Function<InputStream, List<String>> generateTextResultReader = getInputStreamListFunction();
        SseSupport sseSupport = new SseSupport(generateTextResultReader);
        ClientConfigurator clientConfigurator = sseSupport.getClientConfigurator();
        clientConfigurator.customizeClient(builder);

        try (HttpClient client = builder.build()) {
            HttpRequest request = client
                    .createRequest(Method.POST)
                    .header("accepts", MediaType.APPLICATION_JSON)
                    .header("content-type", MediaType.APPLICATION_JSON)
                    .body(jsonPayload);

            // 5) Invoke the call and get the response.
            HttpResponse response = request.execute().toCompletableFuture().get();

            // 6) Print the response headers and body
            Map<String, List<String>> responseHeaders = response.headers();
            System.out.println("HTTP Headers " + responseHeaders);

            InputStream responseBody = response.streamBody().toCompletableFuture().get();
            try (
                    final BufferedReader reader = new BufferedReader(
                            new InputStreamReader(responseBody, StandardCharsets.UTF_8)
                    )
            ) {
                String line;
                while ((line = reader.readLine()) != null) {
                    System.out.println(line);
                }
            }
        } catch (Exception ex) {
            throw ex;
        }
    }

    private static Function<InputStream, List<String>> getInputStreamListFunction() {
        Function<InputStream, List<String>> generateTextResultReader = entityStream -> {
            try (BufferedReader reader =
                         new BufferedReader(new InputStreamReader(entityStream))) {
                String line;
                List<String> generatedTextList = new ArrayList<>();
                while ((line = reader.readLine()) != null) {
                    if (line.isEmpty() || line.startsWith(":")) {
                        continue;
                    }
                    generatedTextList.add(line);
                }
                return generatedTextList;
            } catch (Exception ex) {
                throw new RuntimeException(ex);
            }
        };
        return generateTextResultReader;
    }
}

```

### Using `Langchain` with streaming

**Note:** For streaming, a different endpoint should be used: `/predictWithResponseStream`. You can find more details in the official documentation [here](https://docs.oracle.com/en-us/iaas/Content/data-science/using/model-dep-invoke.htm).

#### Installation
The LangChain OCIModelDeployment integration is part of the [`langchain-community`](https://python.langchain.com/docs/integrations/chat/oci_data_science/)  package.  The chat model integration requires **Python 3.9** or newer. Use the following command to install `langchain-community` along with its required dependencies.

```python
%pip install langgraph "langchain>=0.3" "langchain-community>=0.3" "langchain-openai>=0.2.3" "oracle-ads>2.12"
```

#### Using Langchain for Completion Endpoint
```python
import ads
from langchain_community.llms import OCIModelDeploymentLLM

# Set authentication through ads
# Use resource principal are operating within a
# OCI service that has resource principal based
# authentication configured
ads.set_auth("resource_principal")

# Create an instance of OCI Model Deployment Endpoint
# Replace the endpoint uri and model name with your own
# Using generic class as entry point, you will be able
# to pass model parameters through model_kwargs during
# instantiation.
llm = OCIModelDeploymentLLM(
    endpoint="https://modeldeployment.<region>.oci.customer-oci.com/<md_ocid>/predictWithResponseStream",
    model="odsc-llm",
    streaming=True,
    model_kwargs={
        "temperature": 0.2,
        "max_tokens": 512,
    },  # other model params...
)

# Run the LLM
response = lm.invoke("Who is the first president of United States?")

print(response.content)

```

#### Using Langchain for Chat Completion Endpoint
```python
import ads
from langchain_community.chat_models import ChatOCIModelDeployment

# Use resource principals for authentication
ads.set_auth(auth="resource_principal")

# Initialize the chat model with streaming support
chat = ChatOCIModelDeployment(
    model="odsc-llm",
    endpoint="https://modeldeployment.<region>.oci.customer-oci.com/<md_ocid>/predictWithResponseStream",
    # Optionally you can specify additional keyword arguments for the model.
    max_tokens=1024,
    # Enable streaming
    streaming=True
)

#Invocation
messages = [
    (
        "system",
        "You are a helpful assistant that translates English to French. Translate the user sentence.",
    ),
    ("human", "I love programming."),
]

response = chat.invoke(messages)
print(response.content)
```

***Note:*** Mistral's instruction-tuned models, such as Mistral-7B-Instruct and Mixtral-8x7B-Instruct, do not natively support system prompts using the {"role": "system"} format.

## Multiple Inference endpoints

The support for multiple model deployment inference endpoints ensures flexibility and enables users to perform inferencing on any endpoint, regardless of the endpoint specified during deployment creation.

To access the supported endpoint by TGI/vLLM, you need to include `--request-headers '{"route":"<inference_endpoint>"}'` in the command and update the `--request-body`  according to the endpoint's contract.

```bash
oci raw-request --http-method POST --target-uri <model_deployment_url>/predict --request-headers '{"route":<inference_endpoint>}' --request-body  <request_body> --auth <auth_method>
```

```bash
## If "/v1/completions" was selected during deployment using vLLM SMC and "/v1/chat/completions" endpoint is required later on.

oci raw-request --http-method POST --target-uri  <model_deployment_url>/predict --request-headers '{"route":"/v1/chat/completions"}' --request-body '
      {
          "model": "odsc-llm", # this is a constant
          "messages":[{"role":"user","content":[{"type":"text","text":"Who wrote the book Harry Potter?"}]}],
          "max_tokens": 500,
          "temperature": 0.7,
          "top_p": 0.8,
      }' --auth security_token

```

## Inferencing Embedding model endpoints

Embedding models deployed via AI Quick Actions can be accessed in the similar way as the examples shown above for
generative models, however, the input request format is different. For accessing OpenAI compatible
`/v1/embedding` endpoint for models deployed on vLLM or TEI container, the request format will be:

```python
body = {
    "input": ["What are activation functions?", "What is deep learning?"],
    "model": "odsc-vllm", # use custom name for BYOC TEI
}
```

For more parameters, check the documentation for [vLLM](https://platform.openai.com/docs/api-reference/embeddings/create) and
[Text Embedding Inference (TEI)](https://huggingface.github.io/text-embeddings-inference/#/Text%20Embeddings%20Inference/openai_embed)
inference containers.

## Advanced Configuration Update Options

The available shapes for models in AI Quick Actions are pre-configured for both registration and
deployment for models available in the Model Explorer. However, if you need to add more shapes to the list of
available options, you can do so by updating the relevant configuration file. Currently, this
update option is only available for models that users can register.

#### For Custom Models:
To add shapes for custom models, follow these steps:

1. **Register the model**: Ensure the model is registered via AI Quick Actions UI or CLI.

2. **Navigate to the model's artifact directory**: After registration, locate the directory where the model's artifacts are stored in the object storage.

3. **Create a configuration folder**: Inside the artifact directory, create a new folder named config. For example, if the model path is `oci://<bucket>@namespace/path/to/model/`
then create a folder `oci://<bucket>@namespace/path/to/model/config`.

4. **Add a deployment configuration file**: Within the config folder, create a file named `deployment_config.json` with the following content:


```
{
  "configuration": {
    "VM.Standard.A1.Flex": {
      "parameters": {},
      "shape_info": {
        "configs": [
          {
            "memory_in_gbs": 128,
            "ocpu": 20
          },
          {
            "memory_in_gbs": 256,
            "ocpu": 40
          },
          {
            "memory_in_gbs": 384,
            "ocpu": 60
          },
          {
            "memory_in_gbs": 512,
            "ocpu": 80
          }
        ],
        "type": "CPU"
      }
    }
  },
  "shape": [
    "VM.GPU.A10.1",
    "VM.GPU.A10.2",
    "BM.GPU.A10.4",
    "BM.GPU4.8",
    "BM.GPU.L40S-NC.4",
    "BM.GPU.A100-v2.8",
    "BM.GPU.H100.8",
    "VM.Standard.A1.Flex"
  ]
}
```

This JSON file lists all available GPU and CPU shapes for AI Quick Actions.
The CPU shapes include additional configuration details required for model deployment,
such as memory and OCPU settings.

5. Modify shapes as needed: If you want to add or remove any
[shapes supported](https://docs.oracle.com/en-us/iaas/data-science/using/supported-shapes.htm) by
the OCI Data Science platform, you can directly edit this `deployment_config.json` file.

6. The `configuration` field in this json file can also support parameters for vLLM and TGI inference containers. For example,
if a model can be deployed by either one of these containers, and you want to set the server parameters through configuration file, then
you can add the corresponding shape along with the parameter value inside the `configuration` field. You can achieve the same
using [Advanced Deployment Options](#advanced-deployment-options) from AI Quick Actions UI as well.


```
  "configuration": {
    "VM.GPU.A10.1": {
      "parameters": {
        "TGI_PARAMS": "--max-stop-sequences 6",
        "VLLM_PARAMS": "--max-model-len 4096"
      }
    }
    ...
    ...
  }
```

## Recommended Configurations
| Model | Shape  | Parameters |
|-------|--------|------------|
| Almawave/Velvet-14B | VM.GPU.A10.2 | --trust-remote-code --max-model-len 16000 |
| Almawave/Velvet-14B | BM.GPU.A10.4 |  |
| Almawave/Velvet-14B | BM.GPU.L40S-NC.4 |  |
| Almawave/Velvet-14B | BM.GPU4.8 |  |
| Almawave/Velvet-14B | BM.GPU.A100-v2.8 |  |
| Almawave/Velvet-14B | BM.GPU.H100.8 |  |
| Almawave/Velvet-14B | BM.GPU.H200.8 |  |
| codellama/CodeLlama-13b-Instruct-hf | VM.GPU.A10.2 | --max-model-len 4096 |
| codellama/CodeLlama-13b-Instruct-hf | BM.GPU.A10.4 |  |
| codellama/CodeLlama-13b-Instruct-hf | BM.GPU.L40S-NC.4 |  |
| codellama/CodeLlama-13b-Instruct-hf | VM.Standard.A1.Flex |  |
| codellama/CodeLlama-34b-Instruct-hf | BM.GPU.A10.4 | --max-model-len 4096 |
| codellama/CodeLlama-34b-Instruct-hf | VM.Standard.A1.Flex |  |
| codellama/CodeLlama-7b-Instruct-hf | VM.GPU.A10.1 | --max-model-len 4096 |
| codellama/CodeLlama-7b-Instruct-hf | VM.GPU.A10.2 |  |
| codellama/CodeLlama-7b-Instruct-hf | BM.GPU.A10.4 |  |
| codellama/CodeLlama-7b-Instruct-hf | BM.GPU.L40S-NC.4 |  |
| codellama/CodeLlama-7b-Instruct-hf | VM.Standard.A1.Flex |  |
| core42/jais-13b | BM.GPU4.8 | --tensor-parallel-size 1 |
| core42/jais-13b | BM.GPU.A100-v2.8 | --tensor-parallel-size 1 |
| core42/jais-13b-chat | BM.GPU4.8 | --tensor-parallel-size 1 |
| core42/jais-13b-chat | BM.GPU.A100-v2.8 | --tensor-parallel-size 1 |
| elyza/ELYZA-japanese-Llama-2-13b | VM.GPU.A10.2 | --max-model-len 4096 |
| elyza/ELYZA-japanese-Llama-2-13b | BM.GPU.A10.4 |  |
| elyza/ELYZA-japanese-Llama-2-13b | BM.GPU.L40S-NC.4 |  |
| elyza/ELYZA-japanese-Llama-2-13b-instruct | VM.GPU.A10.2 | --max-model-len 4096 |
| elyza/ELYZA-japanese-Llama-2-13b-instruct | BM.GPU.A10.4 |  |
| elyza/ELYZA-japanese-Llama-2-13b-instruct | BM.GPU.L40S-NC.4 |  |
| elyza/ELYZA-japanese-Llama-2-7b | BM.GPU.A10.4 |  |
| elyza/ELYZA-japanese-Llama-2-7b | BM.GPU.L40S-NC.4 |  |
| elyza/ELYZA-japanese-Llama-2-7b-instruct | BM.GPU.A10.4 |  |
| elyza/ELYZA-japanese-Llama-2-7b-instruct | BM.GPU.L40S-NC.4 |  |
| google/codegemma-1.1-2b | VM.GPU.A10.2 |  |
| google/codegemma-1.1-2b | BM.GPU.A10.4 |  |
| google/codegemma-1.1-7b-it | BM.GPU.A10.4 |  |
| google/codegemma-1.1-7b-it | BM.GPU.L40S-NC.4 |  |
| google/codegemma-2b | VM.GPU.A10.2 |  |
| google/codegemma-2b | BM.GPU.A10.4 |  |
| google/codegemma-7b | BM.GPU.A10.4 |  |
| google/codegemma-7b | BM.GPU.L40S-NC.4 |  |
| google/gemma-1.1-7b-it | BM.GPU.A10.4 |  |
| google/gemma-1.1-7b-it | BM.GPU.L40S-NC.4 |  |
| google/gemma-2b | VM.GPU.A10.2 |  |
| google/gemma-2b | BM.GPU.A10.4 |  |
| google/gemma-2b-it | VM.GPU.A10.2 |  |
| google/gemma-2b-it | BM.GPU.A10.4 |  |
| google/gemma-7b | BM.GPU.A10.4 |  |
| google/gemma-7b | BM.GPU.L40S-NC.4 |  |
| ibm-granite/granite-3.3-2b-instruct | VM.GPU.A10.2 |  |
| ibm-granite/granite-3.3-2b-instruct | BM.GPU.A10.4 |  |
| ibm-granite/granite-3.3-2b-instruct | BM.GPU.L40S-NC.4 |  |
| ibm-granite/granite-3.3-8b-instruct | VM.GPU.A10.1 | --max-model-len 8192 |
| ibm-granite/granite-3.3-8b-instruct | VM.GPU.A10.2 |  |
| ibm-granite/granite-3.3-8b-instruct | BM.GPU.A10.4 |  |
| ibm-granite/granite-3.3-8b-instruct | BM.GPU.L40S-NC.4 |  |
| ibm-granite/granite-3.3-8b-instruct | VM.GPU.A10.1 | --max-model-len 8192 |
| ibm-granite/granite-3.3-8b-instruct | VM.GPU.A10.2 |  |
| ibm-granite/granite-3.3-8b-instruct | BM.GPU.A10.4 |  |
| ibm-granite/granite-3.3-8b-instruct | BM.GPU.L40S-NC.4 |  |
| ibm-granite/granite-3.3-8b-instruct-GGUF | VM.Standard.A1.Flex |  |
| ibm-granite/granite-3.3-8b-instruct-GGUF | VM.Standard.A2.Flex |  |
| ibm-granite/granite-4.0-tiny-base-preview | VM.GPU.A10.2 | --enforce-eager --tensor-parallel-size 2 --tool-call-parser granite --enable-auto-tool-choice |
| ibm-granite/granite-4.0-tiny-base-preview | BM.GPU.A10.4 |  |
| ibm-granite/granite-4.0-tiny-preview | VM.GPU.A10.2 | --enforce-eager --tensor-parallel-size 2 --tool-call-parser granite --enable-auto-tool-choice |
| ibm-granite/granite-4.0-tiny-preview | BM.GPU.A10.4 |  |
| ibm-granite/granite-embedding-278m-multilingual | VM.GPU.A10.2 |  |
| ibm-granite/granite-embedding-278m-multilingual | BM.GPU.A10.4 |  |
| ibm-granite/granite-embedding-278m-multilingual | BM.GPU.L40S-NC.4 |  |
| ibm-granite/granite-speech-3.3-8b | VM.GPU.A10.2 | --trust-remote-code --max-model-len 2048 --tensor-parallel-size 2 |
| ibm-granite/granite-speech-3.3-8b | BM.GPU.H100.8 | --trust-remote-code --tensor-parallel-size 1 |
| ibm-granite/granite-timeseries-ttm-r1 | VM.Standard.E4.Flex |  |
| ibm-granite/granite-timeseries-ttm-r1 | VM.Standard.E5.Flex |  |
| ibm-granite/granite-vision-3.2-2b | VM.GPU.A10.2 |  |
| ibm-granite/granite-vision-3.2-2b | BM.GPU.A10.4 |  |
| ibm-granite/granite-vision-3.2-2b | BM.GPU.L40S-NC.4 |  |
| intfloat/e5-mistral-7b-instruct | VM.GPU.A10.2 |  |
| intfloat/e5-mistral-7b-instruct | BM.GPU.A10.4 |  |
| intfloat/e5-mistral-7b-instruct | BM.GPU.L40S-NC.4 |  |
| meta-llama/Llama-3.2-11B-Vision | BM.GPU.A10.4 | --enforce-eager --max-num-seqs 16 --max-model-len 65536 |
| meta-llama/Llama-3.2-11B-Vision | BM.GPU4.8 | --enforce-eager --max-num-seqs 16 |
| meta-llama/Llama-3.2-11B-Vision | BM.GPU.L40S-NC.4 | --enforce-eager --max-num-seqs 16 |
| meta-llama/Llama-3.2-11B-Vision | BM.GPU.A100-v2.8 | --enforce-eager --max-num-seqs 16 |
| meta-llama/Llama-3.2-11B-Vision | BM.GPU.H100.8 | --enforce-eager --max-num-seqs 16 |
| meta-llama/Llama-3.2-11B-Vision | BM.GPU.H200.8 | --enforce-eager --max-num-seqs 16 |
| meta-llama/Llama-3.2-11B-Vision | BM.GPU.A10.4 | --enforce-eager --max-num-seqs 16 --max-model-len 65536 |
| meta-llama/Llama-3.2-11B-Vision | BM.GPU4.8 | --enforce-eager --max-num-seqs 16 |
| meta-llama/Llama-3.2-11B-Vision | BM.GPU.L40S-NC.4 | --enforce-eager --max-num-seqs 16 |
| meta-llama/Llama-3.2-11B-Vision | BM.GPU.A100-v2.8 | --enforce-eager --max-num-seqs 16 |
| meta-llama/Llama-3.2-11B-Vision | BM.GPU.H100.8 | --enforce-eager --max-num-seqs 16 |
| meta-llama/Llama-3.2-11B-Vision-Instruct | BM.GPU.A10.4 | --enforce-eager --max-num-seqs 16 --max-model-len 65536 |
| meta-llama/Llama-3.2-11B-Vision-Instruct | BM.GPU4.8 | --enforce-eager --max-num-seqs 16 |
| meta-llama/Llama-3.2-11B-Vision-Instruct | BM.GPU.L40S-NC.4 | --enforce-eager --max-num-seqs 16 |
| meta-llama/Llama-3.2-11B-Vision-Instruct | BM.GPU.A100-v2.8 | --enforce-eager --max-num-seqs 16 |
| meta-llama/Llama-3.2-11B-Vision-Instruct | BM.GPU.H100.8 | --enforce-eager --max-num-seqs 16 |
| meta-llama/Llama-3.2-11B-Vision-Instruct | BM.GPU.A10.4 | --enforce-eager --max-num-seqs 16 --max-model-len 65536 |
| meta-llama/Llama-3.2-11B-Vision-Instruct | BM.GPU4.8 | --enforce-eager --max-num-seqs 16 |
| meta-llama/Llama-3.2-11B-Vision-Instruct | BM.GPU.L40S-NC.4 | --enforce-eager --max-num-seqs 16 |
| meta-llama/Llama-3.2-11B-Vision-Instruct | BM.GPU.A100-v2.8 | --enforce-eager --max-num-seqs 16 |
| meta-llama/Llama-3.2-11B-Vision-Instruct | BM.GPU.H100.8 | --enforce-eager --max-num-seqs 16 |
| meta-llama/Llama-3.2-11B-Vision-Instruct | BM.GPU.H200.8 | --enforce-eager --max-num-seqs 16 |
| meta-llama/Llama-3.2-1B | VM.GPU.A10.2 |  |
| meta-llama/Llama-3.2-1B | BM.GPU.A10.4 |  |
| meta-llama/Llama-3.2-1B | BM.GPU.L40S-NC.4 |  |
| meta-llama/Llama-3.2-1B | VM.GPU.A10.2 |  |
| meta-llama/Llama-3.2-1B | BM.GPU.A10.4 |  |
| meta-llama/Llama-3.2-1B | BM.GPU.L40S-NC.4 |  |
| meta-llama/Llama-3.2-1B | VM.Standard.A1.Flex |  |
| meta-llama/Llama-3.2-1B-Instruct | VM.GPU.A10.2 |  |
| meta-llama/Llama-3.2-1B-Instruct | BM.GPU.A10.4 |  |
| meta-llama/Llama-3.2-1B-Instruct | BM.GPU.L40S-NC.4 |  |
| meta-llama/Llama-3.2-1B-Instruct | VM.GPU.A10.2 |  |
| meta-llama/Llama-3.2-1B-Instruct | BM.GPU.A10.4 |  |
| meta-llama/Llama-3.2-1B-Instruct | BM.GPU.L40S-NC.4 |  |
| meta-llama/Llama-3.2-1B-Instruct | VM.Standard.A1.Flex |  |
| meta-llama/Llama-3.2-3B | VM.GPU.A10.1 | --max-model-len 65536 |
| meta-llama/Llama-3.2-3B | VM.GPU.A10.2 |  |
| meta-llama/Llama-3.2-3B | BM.GPU.A10.4 |  |
| meta-llama/Llama-3.2-3B | BM.GPU.L40S-NC.4 |  |
| meta-llama/Llama-3.2-3B | VM.GPU.A10.1 | --max-model-len 65536 |
| meta-llama/Llama-3.2-3B | VM.GPU.A10.2 |  |
| meta-llama/Llama-3.2-3B | BM.GPU.A10.4 |  |
| meta-llama/Llama-3.2-3B | BM.GPU.L40S-NC.4 |  |
| meta-llama/Llama-3.2-3B | VM.Standard.A1.Flex |  |
| meta-llama/Llama-3.2-3B-Instruct | VM.GPU.A10.1 | --max-model-len 65536 |
| meta-llama/Llama-3.2-3B-Instruct | VM.GPU.A10.2 |  |
| meta-llama/Llama-3.2-3B-Instruct | BM.GPU.A10.4 |  |
| meta-llama/Llama-3.2-3B-Instruct | BM.GPU.L40S-NC.4 |  |
| meta-llama/Llama-3.2-3B-Instruct | VM.GPU.A10.1 | --max-model-len 65536 |
| meta-llama/Llama-3.2-3B-Instruct | VM.GPU.A10.2 |  |
| meta-llama/Llama-3.2-3B-Instruct | BM.GPU.A10.4 |  |
| meta-llama/Llama-3.2-3B-Instruct | BM.GPU.L40S-NC.4 |  |
| meta-llama/Llama-3.2-3B-Instruct | VM.Standard.A1.Flex | --tool-call-parser llama3_json --enable-auto-tool-choice |
| meta-llama/Llama-3.2-90B-Vision | BM.GPU4.8 | --enforce-eager --max-num-seqs 32 --max-model-len 6096 |
| meta-llama/Llama-3.2-90B-Vision | BM.GPU.A100-v2.8 | --enforce-eager --max-num-seqs 32 --max-model-len 32768 |
| meta-llama/Llama-3.2-90B-Vision | BM.GPU.H100.8 | --enforce-eager --max-num-seqs 32 --max-model-len 32768 |
| meta-llama/Llama-3.2-90B-Vision | BM.GPU4.8 | --enforce-eager --max-num-seqs 32 --max-model-len 6096 |
| meta-llama/Llama-3.2-90B-Vision | BM.GPU.A100-v2.8 | --enforce-eager --max-num-seqs 32 --max-model-len 32768 |
| meta-llama/Llama-3.2-90B-Vision | BM.GPU.H100.8 | --enforce-eager --max-num-seqs 32 --max-model-len 32768 |
| meta-llama/Llama-3.2-90B-Vision | BM.GPU.H200.8 | --enforce-eager --max-num-seqs 32 --max-model-len 32768 |
| meta-llama/Llama-3.2-90B-Vision-Instruct | BM.GPU4.8 | --enforce-eager --max-num-seqs 32 --max-model-len 6096 |
| meta-llama/Llama-3.2-90B-Vision-Instruct | BM.GPU.A100-v2.8 | --enforce-eager --max-num-seqs 32 --max-model-len 32768 |
| meta-llama/Llama-3.2-90B-Vision-Instruct | BM.GPU.H100.8 | --enforce-eager --max-num-seqs 32 --max-model-len 32768 |
| meta-llama/Llama-3.2-90B-Vision-Instruct | BM.GPU4.8 | --enforce-eager --max-num-seqs 32 --max-model-len 6096 |
| meta-llama/Llama-3.2-90B-Vision-Instruct | BM.GPU.A100-v2.8 | --enforce-eager --max-num-seqs 32 --max-model-len 32768 |
| meta-llama/Llama-3.2-90B-Vision-Instruct | BM.GPU.H100.8 | --enforce-eager --max-num-seqs 32 --max-model-len 32768 |
| meta-llama/Llama-3.2-90B-Vision-Instruct | BM.GPU.H200.8 | --enforce-eager --max-num-seqs 32 --max-model-len 32768 |
| meta-llama/Llama-3.3-70B-Instruct | BM.GPU.A10.4 | --quantization fp8 --gpu-memory-utilization 0.98 --cpu-offload-gb 20 --enforce-eager --max-num-seqs 2 --max_model_len 8192 --tool-call-parser llama3_json --enable-auto-tool-choice |
| meta-llama/Llama-3.3-70B-Instruct | BM.GPU.L40S-NC.4 | --max-model-len 70000 --tool-call-parser llama3_json --enable-auto-tool-choice |
| meta-llama/Llama-3.3-70B-Instruct | VM.Standard.A1.Flex | --tool-call-parser llama3_json --enable-auto-tool-choice |
| meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8 | BM.GPU.H100.8 | --tensor-parallel-size 8 --max-model-len 430000 --gpu-memory-utilization 0.98  --tool-call-parser llama4_json --enable-auto-tool-choice |
| meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8 | BM.GPU.H200.8 | --tensor-parallel-size 8 --max-model-len 430000 --gpu-memory-utilization 0.98  --tool-call-parser llama4_json --enable-auto-tool-choice |
| meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8 | BM.GPU.A100-v2.8 | --tensor-parallel-size 8 --max-model-len 430000 --gpu-memory-utilization 0.98  --tool-call-parser llama4_json --enable-auto-tool-choice |
| meta-llama/Llama-4-Scout-17B-16E | BM.GPU.H100.8 | --tensor-parallel-size 8 --tool-call-parser llama4_json --enable-auto-tool-choice |
| meta-llama/Llama-4-Scout-17B-16E | BM.GPU.H200.8 | --tensor-parallel-size 8 --tool-call-parser llama4_json --enable-auto-tool-choice |
| meta-llama/Llama-4-Scout-17B-16E | BM.GPU.A100-v2.8 | --tensor-parallel-size 8 --tool-call-parser llama4_json --enable-auto-tool-choice |
| meta-llama/Llama-4-Scout-17B-16E-Instruct | BM.GPU.H100.8 | --tensor-parallel-size 8 --max-model-len 1000000 --tool-call-parser llama4_json --enable-auto-tool-choice |
| meta-llama/Llama-4-Scout-17B-16E-Instruct | BM.GPU.H200.8 | --tensor-parallel-size 8 --max-model-len 1000000 --tool-call-parser llama4_json --enable-auto-tool-choice |
| meta-llama/Llama-4-Scout-17B-16E-Instruct | BM.GPU.A100-v2.8 | --tensor-parallel-size 8 --max-model-len 1000000 --tool-call-parser llama4_json --enable-auto-tool-choice |
| meta-llama/Meta-Llama-3-70B | VM.Standard.A1.Flex |  |
| meta-llama/Meta-Llama-3-70B-Instruct | VM.GPU.A10.1 | --max-model-len 4096 |
| meta-llama/Meta-Llama-3-70B-Instruct | VM.GPU.A10.2 |  |
| meta-llama/Meta-Llama-3-70B-Instruct | BM.GPU.A10.4 |  |
| meta-llama/Meta-Llama-3-70B-Instruct | BM.GPU.L40S-NC.4 |  |
| meta-llama/Meta-Llama-3-70B-Instruct | VM.Standard.A1.Flex |  |
| meta-llama/Meta-Llama-3-8B | VM.GPU.A10.2 |  |
| meta-llama/Meta-Llama-3-8B | BM.GPU.A10.4 |  |
| meta-llama/Meta-Llama-3-8B | BM.GPU.L40S-NC.4 |  |
| meta-llama/Meta-Llama-3-8B | VM.Standard.A1.Flex |  |
| meta-llama/Meta-Llama-3-8B-Instruct | VM.GPU.A10.1 | --max-model-len 4096 |
| meta-llama/Meta-Llama-3-8B-Instruct | VM.GPU.A10.2 |  |
| meta-llama/Meta-Llama-3-8B-Instruct | BM.GPU.A10.4 |  |
| meta-llama/Meta-Llama-3-8B-Instruct | BM.GPU.L40S-NC.4 |  |
| meta-llama/Meta-Llama-3-8B-Instruct | VM.Standard.A1.Flex |  |
| meta-llama/Meta-Llama-3.1-405B-FP8 | BM.GPU.H100.8 | --max-model-len 65536 |
| meta-llama/Meta-Llama-3.1-405B-FP8 | BM.GPU.H200.8 | --max-model-len 65536 |
| meta-llama/Meta-Llama-3.1-405B-Instruct-FP8 | BM.GPU.H100.8 | --max-model-len 65536 |
| meta-llama/Meta-Llama-3.1-405B-Instruct-FP8 | BM.GPU.H200.8 | --max-model-len 65536 |
| meta-llama/Meta-Llama-3.1-70B | BM.GPU.A10.4 | --quantization fp8 --gpu-memory-utilization 0.98 --cpu-offload-gb 20 --enforce-eager --max-num-seqs 2 --max_model_len 8192 |
| meta-llama/Meta-Llama-3.1-70B | BM.GPU.L40S-NC.4 | --max-model-len 70000 |
| meta-llama/Meta-Llama-3.1-70B | BM.GPU4.8 |  |
| meta-llama/Meta-Llama-3.1-70B | BM.GPU.A100-v2.8 |  |
| meta-llama/Meta-Llama-3.1-70B | BM.GPU.H100.8 |  |
| meta-llama/Meta-Llama-3.1-70B | BM.GPU.H200.8 |  |
| meta-llama/Meta-Llama-3.1-70B | VM.Standard.A1.Flex |  |
| meta-llama/Meta-Llama-3.1-70B-Instruct | BM.GPU.A10.4 | --quantization fp8 --gpu-memory-utilization 0.98 --cpu-offload-gb 20 --enforce-eager --max-num-seqs 2 --max_model_len 8192 |
| meta-llama/Meta-Llama-3.1-70B-Instruct | BM.GPU.L40S-NC.4 | --max-model-len 70000 |
| meta-llama/Meta-Llama-3.1-70B-Instruct | BM.GPU4.8 |  |
| meta-llama/Meta-Llama-3.1-70B-Instruct | BM.GPU.A100-v2.8 |  |
| meta-llama/Meta-Llama-3.1-70B-Instruct | BM.GPU.H100.8 |  |
| meta-llama/Meta-Llama-3.1-70B-Instruct | BM.GPU.H200.8 |  |
| meta-llama/Meta-Llama-3.1-70B-Instruct | VM.Standard.A1.Flex |  |
| meta-llama/Meta-Llama-3.1-8B | VM.GPU.A10.1 | --max-model-len 4096 |
| meta-llama/Meta-Llama-3.1-8B | VM.GPU.A10.2 |  |
| meta-llama/Meta-Llama-3.1-8B | BM.GPU.A10.4 |  |
| meta-llama/Meta-Llama-3.1-8B | BM.GPU.L40S-NC.4 |  |
| meta-llama/Meta-Llama-3.1-8B | VM.Standard.A1.Flex |  |
| meta-llama/Meta-Llama-3.1-8B-Instruct | VM.GPU.A10.1 | --max-model-len 4096 |
| meta-llama/Meta-Llama-3.1-8B-Instruct | VM.GPU.A10.2 |  |
| meta-llama/Meta-Llama-3.1-8B-Instruct | BM.GPU.A10.4 |  |
| meta-llama/Meta-Llama-3.1-8B-Instruct | BM.GPU.L40S-NC.4 |  |
| meta-llama/Meta-Llama-3.1-8B-Instruct | VM.GPU.A10.1 | --max-model-len 4096 |
| meta-llama/Meta-Llama-3.1-8B-Instruct | VM.GPU.A10.2 |  |
| meta-llama/Meta-Llama-3.1-8B-Instruct | BM.GPU.A10.4 |  |
| meta-llama/Meta-Llama-3.1-8B-Instruct | BM.GPU.L40S-NC.4 |  |
| meta-llama/Meta-Llama-3.1-8B-Instruct | VM.Standard.A1.Flex |  |
| microsoft/phi-2 | VM.GPU.A10.2 |  |
| microsoft/phi-2 | BM.GPU.A10.4 |  |
| microsoft/phi-2 | BM.GPU.L40S-NC.4 |  |
| microsoft/Phi-3-mini-128k-instruct | VM.GPU.A10.2 | --trust-remote-code --max-model-len 4096 |
| microsoft/Phi-3-mini-128k-instruct | BM.GPU.A10.4 | --trust-remote-code --max-model-len 60000 |
| microsoft/Phi-3-mini-128k-instruct | BM.GPU.L40S-NC.4 | --trust-remote-code |
| microsoft/Phi-3-mini-128k-instruct | BM.GPU.A100-v2.8 | --trust-remote-code |
| microsoft/Phi-3-mini-128k-instruct | BM.GPU.H100.8 | --trust-remote-code |
| microsoft/Phi-3-mini-128k-instruct | BM.GPU.H200.8 | --trust-remote-code |
| microsoft/Phi-3-mini-4k-instruct | VM.GPU.A10.2 |  |
| microsoft/Phi-3-mini-4k-instruct | BM.GPU.A10.4 |  |
| microsoft/Phi-3-mini-4k-instruct | BM.GPU.L40S-NC.4 |  |
| microsoft/Phi-3-mini-4k-instruct-gguf-fp16 | VM.Standard.A1.Flex |  |
| microsoft/Phi-3-mini-4k-instruct-gguf-fp16 | VM.Standard.A2.Flex |  |
| microsoft/Phi-3-mini-4k-instruct-gguf-q4 | VM.Standard.A1.Flex |  |
| microsoft/Phi-3-mini-4k-instruct-gguf-q4 | VM.Standard.A2.Flex |  |
| microsoft/Phi-3-vision-128k-instruct | VM.GPU.A10.2 | --trust-remote-code --max-model-len 32000 |
| microsoft/Phi-3-vision-128k-instruct | BM.GPU.A10.4 | --trust-remote-code --max-model-len 60000 |
| microsoft/Phi-3-vision-128k-instruct | BM.GPU.L40S-NC.4 | --trust-remote-code |
| microsoft/Phi-3-vision-128k-instruct | BM.GPU.A100-v2.8 | --trust-remote-code |
| microsoft/Phi-3-vision-128k-instruct | BM.GPU.H100.8 | --trust-remote-code |
| microsoft/Phi-3-vision-128k-instruct | BM.GPU.H200.8 | --trust-remote-code |
| microsoft/Phi-3.5-mini-instruct | VM.GPU.A10.1 | --trust-remote-code --max-model-len 16000 |
| microsoft/Phi-3.5-mini-instruct | VM.GPU.A10.2 |  |
| microsoft/Phi-3.5-mini-instruct | BM.GPU.A10.4 |  |
| microsoft/Phi-3.5-mini-instruct | BM.GPU.L40S-NC.4 |  |
| microsoft/Phi-3.5-mini-instruct | BM.GPU4.8 |  |
| microsoft/Phi-3.5-mini-instruct | BM.GPU.A100-v2.8 |  |
| microsoft/Phi-3.5-mini-instruct | BM.GPU.H100.8 |  |
| microsoft/Phi-3.5-mini-instruct | BM.GPU.H200.8 |  |
| microsoft/Phi-3.5-MoE-instruct | BM.GPU.A10.4 |  |
| microsoft/Phi-3.5-MoE-instruct | BM.GPU.L40S-NC.4 |  |
| microsoft/Phi-3.5-MoE-instruct | BM.GPU4.8 |  |
| microsoft/Phi-3.5-MoE-instruct | BM.GPU.A100-v2.8 |  |
| microsoft/Phi-3.5-MoE-instruct | BM.GPU.H100.8 |  |
| microsoft/Phi-3.5-MoE-instruct | BM.GPU.H200.8 |  |
| microsoft/Phi-3.5-vision-instruct | VM.GPU.A10.1 | --trust-remote-code --max_model_len 16000 |
| microsoft/Phi-3.5-vision-instruct | VM.GPU.A10.2 |  |
| microsoft/Phi-3.5-vision-instruct | BM.GPU.A10.4 |  |
| microsoft/Phi-3.5-vision-instruct | BM.GPU.L40S-NC.4 |  |
| microsoft/Phi-3.5-vision-instruct | BM.GPU4.8 |  |
| microsoft/Phi-3.5-vision-instruct | BM.GPU.A100-v2.8 |  |
| microsoft/Phi-3.5-vision-instruct | BM.GPU.H100.8 |  |
| microsoft/Phi-3.5-vision-instruct | BM.GPU.H200.8 |  |
| microsoft/phi-4 | VM.GPU.A10.1 | --quantization fp8 --enforce-eager --max-num-seqs 2 --max_model_len 8192  --cpu-offload-gb 20 |
| microsoft/phi-4 | BM.GPU.A10.4 |  |
| microsoft/phi-4 | BM.GPU.L40S-NC.4 |  |
| microsoft/phi-4 | BM.GPU4.8 |  |
| microsoft/phi-4 | BM.GPU.A100-v2.8 |  |
| microsoft/phi-4 | BM.GPU.H100.8 |  |
| microsoft/phi-4 | BM.GPU.H200.8 |  |
| microsoft/phi-4 | VM.GPU.A10.1 | --quantization fp8 --enforce-eager --max-num-seqs 2 --max_model_len 8192  --cpu-offload-gb 20 |
| microsoft/phi-4 | BM.GPU.A10.4 |  |
| microsoft/phi-4 | BM.GPU.L40S-NC.4 |  |
| microsoft/phi-4 | BM.GPU4.8 |  |
| microsoft/phi-4 | BM.GPU.A100-v2.8 |  |
| microsoft/phi-4 | BM.GPU.H100.8 |  |
| microsoft/phi-4 | BM.GPU.H200.8 |  |
| microsoft/phi-4-gguf-fp16 | VM.Standard.A1.Flex |  |
| microsoft/phi-4-gguf-fp16 | VM.Standard.A2.Flex |  |
| microsoft/phi-4-gguf-q4 | VM.Standard.A1.Flex |  |
| microsoft/phi-4-gguf-q4 | VM.Standard.A2.Flex |  |
| microsoft/Phi-4-multimodal-instruct | VM.GPU.A10.1 | --gpu-memory-utilization 0.98  --trust-remote-code  --enforce-eager --max-num-seqs 32 --max-model-len 6000  --dtype auto --enable-lora --max-lora-rank 320 --lora-extra-vocab-size 512 --limit-mm-per-prompt audio=1,image=1 --max-loras 2  --lora-modules speech=/opt/ds/model/deployed_model/service_models/Phi-4-multimodal-instruct/0af439b/artifact/speech-lora vision=/opt/ds/model/deployed_model/service_models/Phi-4-multimodal-instruct/0af439b/artifact/vision-lora |
| microsoft/Phi-4-multimodal-instruct | BM.GPU.A10.4 |  |
| microsoft/Phi-4-multimodal-instruct | BM.GPU.L40S-NC.4 |  |
| microsoft/Phi-4-multimodal-instruct | BM.GPU4.8 |  |
| microsoft/Phi-4-multimodal-instruct | BM.GPU.A100-v2.8 |  |
| microsoft/Phi-4-multimodal-instruct | BM.GPU.H100.8 |  |
| microsoft/Phi-4-multimodal-instruct | BM.GPU.H200.8 |  |
| mistralai/Mistral-7B-Instruct-v0.1 | VM.GPU.A10.1 | --max-model-len 4096 |
| mistralai/Mistral-7B-Instruct-v0.1 | VM.GPU.A10.2 |  |
| mistralai/Mistral-7B-Instruct-v0.1 | BM.GPU.A10.4 |  |
| mistralai/Mistral-7B-Instruct-v0.1 | BM.GPU.L40S-NC.4 |  |
| mistralai/Mistral-7B-Instruct-v0.2 | VM.GPU.A10.1 | --max-model-len 4096 |
| mistralai/Mistral-7B-Instruct-v0.2 | VM.GPU.A10.2 |  |
| mistralai/Mistral-7B-Instruct-v0.2 | BM.GPU.A10.4 |  |
| mistralai/Mistral-7B-Instruct-v0.2 | BM.GPU.L40S-NC.4 |  |
| mistralai/Mistral-7B-Instruct-v0.3 | VM.GPU.A10.1 | --max-model-len 4096 |
| mistralai/Mistral-7B-Instruct-v0.3 | VM.GPU.A10.2 | --max-model-len 8192 |
| mistralai/Mistral-7B-Instruct-v0.3 | BM.GPU.A10.4 |  |
| mistralai/Mistral-7B-Instruct-v0.3 | BM.GPU.L40S-NC.4 |  |
| mistralai/Mistral-7B-Instruct-v0.3 | VM.Standard.A1.Flex |  |
| mistralai/Mistral-7B-v0.1 | VM.GPU.A10.1 | --max-model-len 4096 |
| mistralai/Mistral-7B-v0.1 | VM.GPU.A10.2 |  |
| mistralai/Mistral-7B-v0.1 | BM.GPU.A10.4 |  |
| mistralai/Mistral-7B-v0.1 | BM.GPU.L40S-NC.4 |  |
| openai/gpt-oss-120b | BM.GPU.H100.8 | --trust-remote-code --gpu-memory-utilization 0.90  --max-num-seqs 32 --max-model-len 130000 --quantization mxfp4 |
| openai/gpt-oss-120b | BM.GPU.H200.8 | --trust-remote-code --gpu-memory-utilization 0.90  --max-num-seqs 32 --max-model-len 130000 --quantization mxfp4 |
| openai/gpt-oss-120b | BM.GPU.A100-v2.8 | --trust-remote-code --gpu-memory-utilization 0.90  --max-num-seqs 32 --max-model-len 130000 --dtype bfloat16 |
| openai/gpt-oss-120b | BM.GPU.B4.8 | --trust-remote-code --gpu-memory-utilization 0.90  --max-num-seqs 32 --max-model-len 130000 --dtype bfloat16 |
| openai/gpt-oss-120b | BM.GPU4.8 | --trust-remote-code --gpu-memory-utilization 0.90  --max-num-seqs 32 --max-model-len 130000 --dtype bfloat16 |
| openai/gpt-oss-20b | BM.GPU.H100.8 | --trust-remote-code --gpu-memory-utilization 0.90 --max-num-seqs 64 --max-model-len 130000 --quantization mxfp4 |
| openai/gpt-oss-20b | BM.GPU.H200.8 | --trust-remote-code --gpu-memory-utilization 0.90 --max-num-seqs 64 --max-model-len 130000 --quantization mxfp4 |
| openai/gpt-oss-20b | BM.GPU.A10.4 | --trust-remote-code --gpu-memory-utilization 0.90 --max-num-seqs 32 --max_model_len 130000 --dtype bfloat16 |
| openai/gpt-oss-20b | BM.GPU.L40S-NC.4 | --trust-remote-code --gpu-memory-utilization 0.90 --max-num-seqs 32 --max_model_len 130000 --dtype bfloat16 |
| openai/gpt-oss-20b | VM.GPU.A10.2 | --trust-remote-code --gpu-memory-utilization 0.90 --max-num-seqs 5 --max-model-len 8192 --dtype bfloat16 |
| openai/gpt-oss-20b | BM.GPU.A100-v2.8 | --trust-remote-code --gpu-memory-utilization 0.90 --max-num-seqs 64 --max-model-len 130000 --dtype bfloat16 |
| openai/gpt-oss-20b | BM.GPU.B4.8 | --trust-remote-code --gpu-memory-utilization 0.90 --max-num-seqs 32 --max_model_len 130000 --dtype bfloat16 |
| openai/gpt-oss-20b | BM.GPU4.8 | --trust-remote-code --gpu-memory-utilization 0.90 --max-num-seqs 32 --max-model-len 130000 --dtype bfloat16 |
| tiiuae/falcon-7b | VM.GPU.A10.1 | --trust-remote-code |
| tiiuae/falcon-7b | VM.GPU.A10.2 |  |
| tiiuae/falcon-7b | BM.GPU.A10.4 |  |
| tiiuae/falcon-7b | VM.GPU.A10.2 |  |
| tiiuae/falcon-7b | BM.GPU.A10.4 |  |

## Troubleshooting

If the model should fail to deploy, reasons might include lack of GPU availability, or policy permissions.

The logs are a good place to start to diagnose the issue. The logs can be accessed from the UI, or you can
use the ADS Log watcher, see [here](https://accelerated-data-science.readthedocs.io/en/latest/user_guide/cli/opctl/_template/monitoring.html) for more details.

From the **General Information** section the **Log Groups** and **Log** sections are clickable links to
begin the diagnosis.

![General Information](web_assets/gen-info-deployed-model.png)

Table of Contents:

- [Home](README.md)
- [Policies](policies/README.md)
- [CLI](cli-tips.md)
- [Model Fine Tuning](fine-tuning-tips.md)
- [Model Evaluation](evaluation-tips.md)
- [Model Registration](register-tips.md)
- [Multi Modal Inferencing](multimodal-models-tips.md)
- [Private_Endpoints](model-deployment-private-endpoint-tips.md)
- [Tool Calling](model-deployment-tool-calling-tips.md)