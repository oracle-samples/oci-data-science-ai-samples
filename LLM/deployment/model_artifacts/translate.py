"""This module contains a LangChain application to translate English into French

This module requies the following environment variable:
* LLM_ENDPOINT, the model deployment endpoint for LLM.

"""

import os
import ads
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from ads.llm import ChatOCIModelDeploymentVLLM


ads.set_auth(auth="resource_principal")


llm = ChatOCIModelDeploymentVLLM(
    model="odsc-llm",
    endpoint=os.environ["LLM_ENDPOINT"],
    # Optionally you can specify additional keyword arguments for the model, e.g. temperature.
    temperature=0.1,
)


prompt = ChatPromptTemplate.from_messages(
    [
        (
            "human",
            "You are a helpful assistant to translate English into French. Response only the translation.\n"
            "{input}",
        ),
    ]
)

chain = prompt | llm | StrOutputParser()


def invoke(message):
    return chain.invoke({"input": message})
