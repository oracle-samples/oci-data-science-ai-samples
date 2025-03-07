# Tool Calling

The latest [VLLM](ai-quick-actions-containers.md) container in AQUA introduces **tool calling** capabilities. Tool calling allows your model to invoke external functions during inference, enhancing its ability to provide context-specific answers. For more detailed explanations, visit the official VLLM [documentation](https://docs.vllm.ai/en/latest/features/tool_calling.html).


## Enable Tool Calling
To enable tool calling within AQUA, you must specify additional parameters **during model deployment**. In the following example, we are enabling tool calling for the **LLama-3** group of models.

1. Go to the **Advanced Settings** during [model deployment](model-deployment-tips.md).
2. Add the following parameters:

```bash
  --enable-auto-tool-choice
  --tool-call-parser llama3_json
```

By default, if `/v1/completions` endpoint is selected in the AQUA console for your model deployment,
switch to `/v1/chat/completions` endpoint in the Inference Mode under the Advanced options in order to enable tool calling.

Note: Each group of models in VLLM may require a different tool call parser. For the latest list of supported models and parsers, refer to the official VLLM [documentation](https://docs.vllm.ai/en/latest/features/tool_calling.html).


## Usage
Below are Python examples demonstrating how to set up and utilize tool calling with the VLLM container and the **LLama-3** model in AQUA.

### With LangChain

This code snippet uses the `langchain_community.chat_models.ChatOCIModelDeployment` class and a simple tool function to query an external exchange rate API. Alternatively, you can use the `ads.llm.ChatOCIModelDeployment` class, which may include the most recent code updates. For more details visit the ADS official [documentation](https://accelerated-data-science.readthedocs.io/en/latest/user_guide/large_language_model/langchain_models.html#tool-calling)

Note: The `LangChain` integration requires `python>=3.9`, `langchain>=0.3` and `langchain-openai`.

```bash
pip install oracle-ads[llm] langchain langchain-openai
```

```python
import os
import requests

import ads
# from ads.llm import ChatOCIModelDeployment
from langchain_community.chat_models import ChatOCIModelDeployment
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import create_tool_calling_agent, AgentExecutor

ads.set_auth("resource_principal")

llm = ChatOCIModelDeployment(
    model="odsc-llm",
    endpoint= f"https://modeldeployment.oci.customer-oci.com/<OCID>/predict",
    tool_choice="auto",
)

@tool
def get_exchange_rate(currency:str) -> str:
    """Obtain the current exchange rates of currency in ISO 4217 Three Letter Currency Code"""

    response = requests.get(f"https://open.er-api.com/v6/latest/{currency}")
    return response.json()

tools = [get_exchange_rate]
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful assistant"),
        ("placeholder", "{chat_history}"),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ]
)

agent = create_tool_calling_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, return_intermediate_steps=True)

agent_executor.invoke({"input": "what's the currency conversion of USD to RUB"})
```

You can also specify a Chat Template tailored for a specific model. A list of pre-configured Chat Templates provided by VLLM is available in their GitHub repository. Below is an example demonstrating how to utilize a Chat Template capability.

```python

# The helper method to read the template file
def read_template(filename):
  with open(filename, mode="r", encoding="utf-8") as f:
      return f.read()

llm = ChatOCIModelDeployment(
    model="odsc-llm",
    endpoint= f"https://modeldeployment.oci.customer-oci.com/<OCID>/predict",
    tool_choice="auto",
    chat_template=read_template("tool_chat_template_llama3.2_json.jinja")
)
```

### Without Additional Libraries
In this example, the only library you need to install is `oracle-ads`, which is required for authentication purposes.
You can find more details about authentication [here](https://accelerated-data-science.readthedocs.io/en/latest/user_guide/cli/authentication.html). Additionally, ensure you have the necessary [policies](https://docs.oracle.com/en-us/iaas/data-science/using/model-dep-policies-auth.htm) in place to access the OCI Data Science Model Deployment endpoint.


```bash
pip install oracle-ads
```

```python
import json

import ads
import requests

ads.set_auth("resource_principal")

auth = ads.common.auth.default_signer()["signer"]

endpoint = ("https://modeldeployment.oci.customer-oci.com/<OCID>/predict",)


def read_template(filename):
    with open(filename, mode="r", encoding="utf-8") as f:
        return f.read()


# Now, simulate a tool call
def get_current_weather(city: str, state: str, unit: "str"):
    """returns the weather data for a specific location"""
    return (
        "The weather in Dallas, Texas is 85 degrees fahrenheit. It is "
        "partly cloudly, with highs in the 90's."
    )


tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "Get the current weather in a given location",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "The city to find the weather for, e.g. 'San Francisco'",
                    },
                    "state": {
                        "type": "string",
                        "description": "the two-letter abbreviation for the state that the city is"
                        " in, e.g. 'CA' which would mean 'California'",
                    },
                    "unit": {
                        "type": "string",
                        "description": "The unit to fetch the temperature in",
                        "enum": ["celsius", "fahrenheit"],
                    },
                },
                "required": ["city", "state", "unit"],
            },
        },
    }
]

body = {
    "model": "odsc-llm",  # this is a constant
    "max_tokens": 500,
    "temperature": 0.7,
    "top_p": 0.8,
    "tools": tools,
    "tool_choice": "auto",
}


messages = [
    {
        "role": "system",
        "content": "You are a helpful assistant with tool calling capabilities. Only reply with a tool call if the function exists in the library provided by the user. If it doesn't exist, just reply directly in natural language.",
    },
    {
        "role": "user",
        "content": "Can you tell me what the temperate will be in Dallas, in fahrenheit?",
    },
]

body["messages"] = messages

# use vLLM offical jinja template
body["chat_template"] = read_template("tool_chat_template_llama3.1_json.jinja")

route = "/v1/chat/completions"

headers = {
    "Content-Type": "application/json",
    "enable-streaming": "true",
    "Accept": "text/event-stream",
    "route": route,
}
response = requests.post(endpoint, json=body, auth=auth, headers=headers).json()

print(response)

# add this to invoke the tool call and have model interpret tool call response

tool_call = response["choices"][0]["message"]["tool_calls"][0]
args = json.loads(tool_call["function"]["arguments"])

result = get_current_weather(**args)

messages.append(response["choices"][0]["message"])

messages.append(
    {"role": "tool", "tool_call_id": tool_call["id"], "content": str(result)}
)

body["messages"] = messages

headers = {
    "Content-Type": "application/json",
    "enable-streaming": "true",
    "Accept": "text/event-stream",
    "route": route,
}

response = requests.post(endpoint, json=body, auth=auth, headers=headers).json()

print(response)
```


