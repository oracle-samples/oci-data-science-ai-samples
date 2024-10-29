"""LangGraph application containing a research node and a chat node
Adapted from https://langchain-ai.github.io/langgraph/tutorials/multi_agent/multi-agent-collaboration/

This module requires the following environment variable:
* PROJECT_COMPARTMENT_OCID, the compartment OCID for access OCI Generative AI service.

Custom networking with internet access is required for this app to run Tavily search tool.

For more information on custom networking, see:
https://docs.oracle.com/en-us/iaas/data-science/using/model-dep-create-cus-net.htm
"""

import base64
import os
import operator
import tempfile
import traceback
from typing import Annotated, Sequence
from typing_extensions import TypedDict

from ads.config import COMPARTMENT_OCID
from langchain_community.chat_models.oci_generative_ai import ChatOCIGenAI
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    HumanMessage,
    ToolMessage,
)
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool
from langchain_experimental.utilities import PythonREPL
from langgraph.prebuilt import ToolNode
from langgraph.graph import START, END, StateGraph

# Use LLM from OCI generative AI service
llm = ChatOCIGenAI(
    model_id="cohere.command-r-plus",
    # Service endpoint is not needed if the generative AI is available in the same region.
    # service_endpoint="https://inference.generativeai.us-chicago-1.oci.oraclecloud.com",
    compartment_id=COMPARTMENT_OCID,
    model_kwargs={"temperature": 0, "max_tokens": 4000},
    auth_type="RESOURCE_PRINCIPAL",
)

# Search tool
tavily_tool = TavilySearchResults(max_results=5)

# Python code execution tool
repl = PythonREPL()


@tool
def python_repl(
    code: Annotated[str, "The python code to execute to generate your chart."],
):
    """Use this to execute python code. If you want to see the output of a value,
    you should print it out with `print(...)`. This is visible to the user."""
    try:
        # Set the timeout so the code will be run in a separated process
        # This will avoid the code changing variables in the current process.
        result = repl.run(code, timeout=30)
    except BaseException as e:
        return f"Failed to execute. Error: {repr(e)}"
    result_str = f"Successfully executed:\n```python\n{code}\n```\nStdout: {result}"
    return result_str


class AgentState(TypedDict):
    """Represents the state of the agents"""

    messages: Annotated[Sequence[BaseMessage], operator.add]
    sender: str


class AgentNode:
    """Represents an agent node."""

    def __init__(self, name, llm, system_message, tools=None) -> None:
        self.name = name
        instructions = (
            "You are a helpful AI agent,"
            " collaborating with other agents work on a task step by step."
            " If you are unable to fully finish it, another agent may help where you left off."
            " Execute what you can to make progress."
            " If you or any of the other assistants have the final answer,"
            " or the team cannot make any progress,"
            " prefix your response with FINAL ANSWER so the team knows to stop."
        )
        if tools:
            tool_names = ", ".join([tool.name for tool in tools])
            instructions += f" You have access to the following tools: {tool_names}.\n"
            llm = llm.bind_tools(tools)
        instructions += system_message
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    instructions,
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )
        prompt = prompt.partial(system_message=system_message)
        self.agent = prompt | llm

    def __call__(self, state: AgentState) -> dict:
        result = self.agent.invoke(state)
        # We convert the agent output into a format that is suitable to append to the global state
        if not isinstance(result, ToolMessage):
            result = AIMessage(**result.dict(exclude={"type", "name"}), name=self.name)
        return {
            "messages": [result],
            # Since we have a strict workflow, we can
            # track the sender so we know who to pass to next.
            "sender": self.name,
        }


# Nodes
RESEARCH_NODE = "research_node"
CHART_NODE = "chart_node"

# research
research_node = AgentNode(
    RESEARCH_NODE,
    llm,
    system_message="You should provide accurate data for plotting the chart.",
    tools=[tavily_tool],
)


# temp dir for saving the chart
# Each thread will get a different temp dir
tmp_dir = tempfile.TemporaryDirectory()
print(f"Temp directory: {tmp_dir.name}")
tmp_file = os.path.join(tmp_dir.name, "chart.png")
# chart
chart_node = AgentNode(
    CHART_NODE,
    llm,
    system_message=(
        f"Run Python code to plot the chart and save it to a file named {tmp_file}. "
        "Response FINAL ANSWER once the chart is plotted successfully."
    ),
    tools=[python_repl],
)

search_tool = ToolNode([tavily_tool])
chart_tool = ToolNode([python_repl])
SEARCH_TOOL = "search_tool"
CHART_TOOL = "chart_tool"


def research_path(state):
    """Router for research_node"""
    messages = state["messages"]
    last_message = messages[-1]
    if "FINAL ANSWER" in last_message.content:
        # Any agent decided the work is done
        return END
    if last_message.tool_calls:
        return SEARCH_TOOL
    else:
        return CHART_NODE


def chart_path(state):
    """Router for chart_node."""
    messages = state["messages"]
    last_message = messages[-1]
    if "FINAL ANSWER" in last_message.content:
        # Any agent decided the work is done
        return END
    if last_message.tool_calls:
        return CHART_TOOL
    else:
        return RESEARCH_NODE


workflow = StateGraph(AgentState)

workflow.add_node(CHART_NODE, chart_node)
workflow.add_node(RESEARCH_NODE, research_node)

workflow.add_node(SEARCH_TOOL, search_tool)
workflow.add_node(CHART_TOOL, chart_tool)

workflow.add_edge(START, RESEARCH_NODE)

workflow.add_conditional_edges(
    RESEARCH_NODE, research_path, {n: n for n in [SEARCH_TOOL, CHART_NODE, END]}
)
workflow.add_conditional_edges(
    CHART_NODE, chart_path, {n: n for n in [CHART_TOOL, RESEARCH_NODE, END]}
)


workflow.add_edge(CHART_TOOL, CHART_NODE)
workflow.add_edge(SEARCH_TOOL, RESEARCH_NODE)


graph = workflow.compile()


def invoke(message):
    """Invokes the graph."""
    events = graph.stream(
        {
            "messages": [HumanMessage(content=message)],
        },
        # Maximum number of steps to take in the graph
        {"recursion_limit": 10},
    )

    # Print and save the messages
    messages = []
    for event in events:
        for node, value in event.items():
            print(node)
            print("-" * 50)
            message = value["messages"][-1].content
            messages.append(message)
            print(message)
        print("=" * 50)

    # Load the chart and encode it with base64
    if os.path.exists(tmp_file):
        with open(tmp_file, mode="rb") as f:
            chart = base64.b64encode(f.read()).decode()
            print(f"Loaded chart from {tmp_file}")
        try:
            os.remove(tmp_file)
        except Exception:
            print(f"Failed to remove file {tmp_file}.")
            traceback.print_exc()
    else:
        chart = None
    return {"chart": chart, "messages": messages}
