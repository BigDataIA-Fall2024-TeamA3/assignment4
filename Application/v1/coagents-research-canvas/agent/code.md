# backend code files
#coagents-research-canvas/agent/research_canvas/agent.py
"""
This is the main entry point for the AI.
It defines the workflow graph and the entry point for the agent.
"""
# pylint: disable=line-too-long, unused-import
import json
from typing import cast

from langchain_core.messages import AIMessage, ToolMessage
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from research_canvas.state import AgentState
from research_canvas.download import download_node
from research_canvas.chat import chat_node
from research_canvas.search import search_node
from research_canvas.delete import delete_node, perform_delete_node

# Define a new graph
workflow = StateGraph(AgentState)
workflow.add_node("download", download_node)
workflow.add_node("chat_node", chat_node)
workflow.add_node("search_node", search_node)
workflow.add_node("delete_node", delete_node)
workflow.add_node("perform_delete_node", perform_delete_node)

def route(state):
    """Route after the chat node."""

    messages = state.get("messages", [])
    if messages and isinstance(messages[-1], AIMessage):
        ai_message = cast(AIMessage, messages[-1])

        if ai_message.tool_calls and ai_message.tool_calls[0]["name"] == "Search":
            return "search_node"
        if ai_message.tool_calls and ai_message.tool_calls[0]["name"] == "DeleteResources":
            return "delete_node"
    if messages and isinstance(messages[-1], ToolMessage):
        return "chat_node"

    return END


memory = MemorySaver()
workflow.set_entry_point("download")
workflow.add_edge("download", "chat_node")
workflow.add_conditional_edges("chat_node", route, ["search_node", "chat_node", "delete_node", END])
workflow.add_edge("delete_node", "perform_delete_node")
workflow.add_edge("perform_delete_node", "chat_node")
workflow.add_edge("search_node", "download")
graph = workflow.compile(checkpointer=memory, interrupt_after=["delete_node"])


# coagents-research-canvas/agent/research_canvas/chat.py
"""Chat Node"""

from typing import List, cast
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import SystemMessage, AIMessage, ToolMessage
from langchain.tools import tool
from copilotkit.langchain import copilotkit_customize_config
from research_canvas.state import AgentState
from research_canvas.model import get_model
from research_canvas.download import get_resource

@tool
def Search(queries: List[str]): # pylint: disable=invalid-name,unused-argument
    """A list of one or more search queries to find good resources to support the research."""

@tool
def WriteReport(report: str): # pylint: disable=invalid-name,unused-argument
    """Write the research report."""

@tool
def WriteResearchQuestion(research_question: str): # pylint: disable=invalid-name,unused-argument
    """Write the research question."""

@tool
def DeleteResources(urls: List[str]): # pylint: disable=invalid-name,unused-argument
    """Delete the URLs from the resources."""


async def chat_node(state: AgentState, config: RunnableConfig):
    """
    Chat Node
    """

    config = copilotkit_customize_config(
        config,
        emit_intermediate_state=[{
            "state_key": "report",
            "tool": "WriteReport",
            "tool_argument": "report",
        }, {
            "state_key": "research_question",
            "tool": "WriteResearchQuestion",
            "tool_argument": "research_question",
        }],
        emit_tool_calls="DeleteResources"
    )

    state["resources"] = state.get("resources", [])
    research_question = state.get("research_question", "")
    report = state.get("report", "")

    resources = []

    for resource in state["resources"]:
        content = get_resource(resource["url"])
        if content == "ERROR":
            continue
        resources.append({
            **resource,
            "content": content
        })

    model = get_model(state)
    # Prepare the kwargs for the ainvoke method
    ainvoke_kwargs = {}
    if model.__class__.__name__ in ["ChatOpenAI"]:
        ainvoke_kwargs["parallel_tool_calls"] = False

    response = await model.bind_tools(
        [
            Search,
            WriteReport,
            WriteResearchQuestion,
            DeleteResources,
        ],
        **ainvoke_kwargs  # Pass the kwargs conditionally
    ).ainvoke([
        SystemMessage(
            content=f"""
            You are a research assistant. You help the user with writing a research report.
            Do not recite the resources, instead use them to answer the user's question.
            You should use the search tool to get resources before answering the user's question.
            If you finished writing the report, ask the user proactively for next steps, changes etc, make it engaging.
            To write the report, you should use the WriteReport tool. Never EVER respond with the report, only use the tool.
            If a research question is provided, YOU MUST NOT ASK FOR IT AGAIN.

            This is the research question:
            {research_question}

            This is the research report:
            {report}

            Here are the resources that you have available:
            {resources}
            """
        ),
        *state["messages"],
    ], config)

    ai_message = cast(AIMessage, response)

    if ai_message.tool_calls:
        if ai_message.tool_calls[0]["name"] == "WriteReport":
            report = ai_message.tool_calls[0]["args"].get("report", "")
            return {
                "report": report,
                "messages": [ai_message, ToolMessage(
                    tool_call_id=ai_message.tool_calls[0]["id"],
                    content="Report written."
                )]
            }
        if ai_message.tool_calls[0]["name"] == "WriteResearchQuestion":
            return {
                "research_question": ai_message.tool_calls[0]["args"]["research_question"],
                "messages": [ai_message, ToolMessage(
                    tool_call_id=ai_message.tool_calls[0]["id"],
                    content="Research question written."
                )]
            }

    return {
        "messages": response
    }


# coagents-research-canvas/agent/research_canvas/delete.py
"""Delete Resources"""

import json
from typing import cast
from research_canvas.state import AgentState
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import ToolMessage, AIMessage
async def delete_node(state: AgentState, config: RunnableConfig): # pylint: disable=unused-argument
    """
    Delete Node
    """
    return state

async def perform_delete_node(state: AgentState, config: RunnableConfig): # pylint: disable=unused-argument
    """
    Perform Delete Node
    """
    ai_message = cast(AIMessage, state["messages"][-2])
    tool_message = cast(ToolMessage, state["messages"][-1])
    if tool_message.content == "YES":
        if ai_message.tool_calls:
            urls = ai_message.tool_calls[0]["args"]["urls"]
        else:
            parsed_tool_call = json.loads(ai_message.additional_kwargs["function_call"]["arguments"])
            urls = parsed_tool_call["urls"]

        state["resources"] = [
            resource for resource in state["resources"] if resource["url"] not in urls
        ]

    return state


# coagents-research-canvas/agent/research_canvas/model.py
"""
This module provides a function to get a model based on the configuration.
"""
import os
from typing import cast, Any
from langchain_core.language_models.chat_models import BaseChatModel
from research_canvas.state import AgentState

def get_model(state: AgentState) -> BaseChatModel:
    """
    Get a model based on the environment variable.
    """

    state_model = state.get("model")
    model = os.getenv("MODEL", state_model)

    print(f"Using model: {model}")

    if model == "openai":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(temperature=0, model="gpt-4o-mini")
    if model == "anthropic":
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(
            temperature=0,
            model_name="claude-3-5-sonnet-20240620",
            timeout=None,
            stop=None
        )
    # if model == "google_genai":
    #     from langchain_google_genai import ChatGoogleGenerativeAI
    #     return ChatGoogleGenerativeAI(
    #         temperature=0,
    #         model="gemini-1.5-pro",
    #         api_key=cast(Any, os.getenv("GOOGLE_API_KEY")) or None
    #     )

    raise ValueError("Invalid model specified")


# coagents-research-canvas/agent/research_canvas/model.py
"""
This module provides a function to get a model based on the configuration.
"""
import os
from typing import cast, Any
from langchain_core.language_models.chat_models import BaseChatModel
from research_canvas.state import AgentState

def get_model(state: AgentState) -> BaseChatModel:
    """
    Get a model based on the environment variable.
    """

    state_model = state.get("model")
    model = os.getenv("MODEL", state_model)

    print(f"Using model: {model}")

    if model == "openai":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(temperature=0, model="gpt-4o-mini")
    if model == "anthropic":
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(
            temperature=0,
            model_name="claude-3-5-sonnet-20240620",
            timeout=None,
            stop=None
        )
    # if model == "google_genai":
    #     from langchain_google_genai import ChatGoogleGenerativeAI
    #     return ChatGoogleGenerativeAI(
    #         temperature=0,
    #         model="gemini-1.5-pro",
    #         api_key=cast(Any, os.getenv("GOOGLE_API_KEY")) or None
    #     )

    raise ValueError("Invalid model specified")


# coagents-research-canvas/agent/research_canvas/search.py
"""
The search node is responsible for searching the internet for information.
"""

import os
from typing import cast, List
from pydantic import BaseModel, Field
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import AIMessage, ToolMessage, SystemMessage
from langchain.tools import tool
from tavily import TavilyClient
from copilotkit.langchain import copilotkit_emit_state, copilotkit_customize_config
from research_canvas.state import AgentState
from research_canvas.model import get_model

class ResourceInput(BaseModel):
    """A resource with a short description"""
    url: str = Field(description="The URL of the resource")
    title: str = Field(description="The title of the resource")
    description: str = Field(description="A short description of the resource")

@tool
def ExtractResources(resources: List[ResourceInput]): # pylint: disable=invalid-name,unused-argument
    """Extract the 3-5 most relevant resources from a search result."""

tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

async def search_node(state: AgentState, config: RunnableConfig):
    """
    The search node is responsible for searching the internet for resources.
    """
    ai_message = cast(AIMessage, state["messages"][-1])

    state["resources"] = state.get("resources", [])
    state["logs"] = state.get("logs", [])
    queries = ai_message.tool_calls[0]["args"]["queries"]

    for query in queries:
        state["logs"].append({
            "message": f"Search for {query}",
            "done": False
        })

    await copilotkit_emit_state(config, state)

    search_results = []

    for i, query in enumerate(queries):
        response = tavily_client.search(query)
        search_results.append(response)
        state["logs"][i]["done"] = True
        await copilotkit_emit_state(config, state)

    config = copilotkit_customize_config(
        config,
        emit_intermediate_state=[{
            "state_key": "resources",
            "tool": "ExtractResources",
            "tool_argument": "resources",
        }],
    )

    model = get_model(state)
    ainvoke_kwargs = {}
    if model.__class__.__name__ in ["ChatOpenAI"]:
        ainvoke_kwargs["parallel_tool_calls"] = False

    # figure out which resources to use
    response = await model.bind_tools(
        [ExtractResources],
        tool_choice="ExtractResources",
        **ainvoke_kwargs
    ).ainvoke([
        SystemMessage(
            content="""
            You need to extract the 3-5 most relevant resources from the following search results.
            """
        ),
        *state["messages"],
        ToolMessage(
        tool_call_id=ai_message.tool_calls[0]["id"],
        content=f"Performed search: {search_results}"
    )
    ], config)

    state["logs"] = []
    await copilotkit_emit_state(config, state)

    ai_message_response = cast(AIMessage, response)
    resources = ai_message_response.tool_calls[0]["args"]["resources"]

    state["resources"].extend(resources)

    state["messages"].append(ToolMessage(
        tool_call_id=ai_message.tool_calls[0]["id"],
        content=f"Added the following resources: {resources}"
    ))

    return state



# coagents-research-canvas/agent/research_canvas/state.py
"""
This is the state definition for the AI.
It defines the state of the agent and the state of the conversation.
"""

from typing import List, TypedDict
from langgraph.graph import MessagesState

class Resource(TypedDict):
    """
    Represents a resource. Give it a good title and a short description.
    """
    url: str
    title: str
    description: str

class Log(TypedDict):
    """
    Represents a log of an action performed by the agent.
    """
    message: str
    done: bool

class AgentState(MessagesState):
    """
    This is the state of the agent.
    It is a subclass of the MessagesState class from langgraph.
    """
    model: str
    research_question: str
    report: str
    resources: List[Resource]
    logs: List[Log]
