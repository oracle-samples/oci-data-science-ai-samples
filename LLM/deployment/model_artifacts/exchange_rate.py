"""This module contains a LangChain agent example to answer question about currency exchange.

It uses OCI Generative AI as the LLM to:
1. Generate arguments for tool calling for obtaining the exchange rate.
2. Process the tool calling results (exchange rates in JSON payload).
3. Answer the user's question.

This module requires the following environment variable:
* PROJECT_COMPARTMENT_OCID, the compartment OCID for access OCI Generative AI service.

By default, OCI model deployment can only access the OCI Generative AI endpoints
within the same region. Custom networking for the model deployment is required 
if you deploy the app in a different region.

Custom networking with internet access is required for this app to run the get_exchange_rate() function.

For more information on custom networking, see:
https://docs.oracle.com/en-us/iaas/data-science/using/model-dep-create-cus-net.htm

"""

import os
import requests
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_community.chat_models.oci_generative_ai import ChatOCIGenAI
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate


# Use LLM from OCI generative AI service
llm = ChatOCIGenAI(
    model_id="cohere.command-r-plus",
    # Service endpoint is not needed if the generative AI is available in the same region.
    # service_endpoint="https://inference.generativeai.us-chicago-1.oci.oraclecloud.com",
    # Make sure you configure custom networking if you use a service endpoint in a different region.
    compartment_id=os.environ["PROJECT_COMPARTMENT_OCID"],
    model_kwargs={"temperature": 0, "max_tokens": 4000},
    auth_type="RESOURCE_PRINCIPAL",
)


@tool
def get_exchange_rate(currency: str) -> str:
    """Obtain the current exchange rates of a currency to other currencies.
    
    Parameters
    ----------
    currency : str
        Currency in ISO 4217 3-letter currency code
        
    Returns
    -------
    dict:
        The value of `rates` is a dictionary contains the exchange rates to other currencies,
        in which the keys are the ISO 4217 3-letter currency codes.
    """

    response = requests.get(f"https://open.er-api.com/v6/latest/{currency}", timeout=10)
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
agent_executor = AgentExecutor(
    agent=agent, tools=tools, verbose=True, return_intermediate_steps=False
)


def invoke(message):
    return agent_executor.invoke({"input": message})
