# LangChain Translation App with Prompt Template

LangChain is a framework for developing applications powered by language models. The [Oracle Accelerated Data Science (ADS)](https://accelerated-data-science.readthedocs.io/en/latest/index.html) library provides LangChain integration with models deployed using OCI Data Science Model Deployment. 

In this tutorial, we will show you how to build a LangChain translation app with prompt template and LLM deployed on OCI Data Science to translate from English into French.

## Prerequisites

Python 3.9 or newer is required to use the latest feature in LangChain. Building LangChain applications also requires some dependencies, including LangChain and [Oracle Accelerated Data Science (ADS)](https://accelerated-data-science.readthedocs.io/en/latest/index.html) library. You can install them with the following command:

```bash
pip install langgraph "langchain>=0.3" "langchain-community>=0.3" "langchain-openai>=0.2.3" "oracle-ads>2.12"
```

## Authentication

You can set the authentication through either ADS or environment variables. When you’re working in a Data Science notebook session, you can use resource principals to access other OCI resources. To use the resource principal to authenticate, run the following command:

```python
import ads

ads.set_auth("resource_principal")
```
For more options, see [Oracle ADS Authentication](accelerated-data-science.readthedocs.io/en/latest/user_guide/cli/authentication.html).

## LangChain Application

Here are the steps to create the LangChain application:

### Create a Prompt Template

Next, create a prompt template. The following example shows a template for a LangChain application translating English into French:

```
from langchain.prompts import PromptTemplate
from langchain.schema.runnable import RunnableParallel, RunnablePassthrough

map_input = RunnableParallel(text=RunnablePassthrough())
template = PromptTemplate.from_template("Translate the text into French.\nText:{text}\nFrench translation: ")
```

### Initialize a LangChain OCI Model Deployment Endpoint Object

Create a OCI Model Deployment endpoint object based on the inference framework you chose. For example, to use the model deployed with vLLM as the inference framework, use the following command:

```python
from langchain_community.llms import OCIModelDeploymentVLLM

llm = OCIModelDeploymentVLLM(
    model="odsc-llm",
    endpoint="OCI_MODEL_DEPLOYMENT_URL",
)
```

Check out the [LangChain documentation](https://python.langchain.com/docs/integrations/llms/oci_model_deployment_endpoint/) for more details.

### Create an LLM chain

Pass the created prompt and the OCI Model Deployment endpoint as arguments to your LLM chain.
```
chain = map_input | template | llm
```

### Invoke the LLM

Use the invoke method to invoke your LLM.
```
chain.invoke("Oracle offers a comprehensive and fully integrated stack of cloud applications and cloud platform services.")
```

The following cell shows the result from Llama 2-13B:
```
Oracle propose une stack complète et intégralement integrée de applications cloud et de services de plateforme cloud.\n
```
