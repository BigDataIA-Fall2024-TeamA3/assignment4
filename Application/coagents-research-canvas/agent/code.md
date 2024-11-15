#coagents-research-canvas/agent/research_canvas/agent.py

"""
This is the main entry point for the AI.
It defines the workflow graph and the entry point for the agent.
"""

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
from research_canvas.arxiv_agent import arxiv_search_node
from research_canvas.document_selection import document_selection_node
from research_canvas.rag_agent import rag_node

# Define an exception handler decorator
def node_exception_handler(node_func):
    def wrapper(state):
        try:
            return node_func(state)
        except Exception as e:
            # Log the exception
            print(f"Exception in {node_func.__name__}: {e}")
            # Optionally, store the error in the state
            state['errors'] = state.get('errors', []) + [f"{node_func.__name__}: {str(e)}"]
            # Return the state to allow the workflow to continue
            return state
    return wrapper

# Define a new graph
workflow = StateGraph(AgentState)
workflow.add_node("document_selection", node_exception_handler(document_selection_node))
workflow.add_node("arxiv_search", node_exception_handler(arxiv_search_node))
workflow.add_node("web_search", node_exception_handler(search_node))
workflow.add_node("download", node_exception_handler(download_node))
workflow.add_node("rag_agent", node_exception_handler(rag_node))
workflow.add_node("chat_node", node_exception_handler(chat_node))
workflow.add_node("delete_node", node_exception_handler(delete_node))
workflow.add_node("perform_delete_node", node_exception_handler(perform_delete_node))

def route(state):
    """Route based on the current state and messages."""
    # Check if any errors have occurred
    errors = state.get('errors', [])
    if errors:
        # Optionally handle errors, e.g., log them or decide to proceed or terminate
        print(f"Errors in state: {errors}")
        # For now, we proceed as normal

    messages = state.get("messages", [])
    if messages and isinstance(messages[-1], AIMessage):
        ai_message = cast(AIMessage, messages[-1])

        if ai_message.tool_calls:
            tool_name = ai_message.tool_calls[0]["name"]
            if tool_name == "Search":
                return "web_search"
            elif tool_name == "ArxivSearch":
                return "arxiv_search"
            elif tool_name == "DeleteResources":
                return "delete_node"
            elif tool_name == "RAG":
                return "rag_agent"

    if messages and isinstance(messages[-1], ToolMessage):
        return "chat_node"

    return END

memory = MemorySaver()
workflow.set_entry_point("document_selection")
workflow.add_edge("document_selection", "chat_node")
workflow.add_edge("download", "chat_node")
workflow.add_conditional_edges(
    "chat_node",
    route,
    ["web_search", "arxiv_search", "rag_agent", "delete_node", "chat_node", END]
)
workflow.add_edge("web_search", "download")
workflow.add_edge("arxiv_search", "download")
workflow.add_edge("rag_agent", "chat_node")
workflow.add_edge("delete_node", "perform_delete_node")
workflow.add_edge("perform_delete_node", "chat_node")
graph = workflow.compile(checkpointer=memory, interrupt_after=["delete_node"])

# coagents-research-canvas/agent/research_canvas/api.py

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Allow all origins for development. Restrict in production.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# coagents-research-canvas/agent/research_canvas/agents/arxiv_agent.py

import arxiv
from typing import List, cast
from langchain.tools import tool
from research_canvas.state import AgentState
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import AIMessage, ToolMessage

@tool
def ArxivSearch(query: str):
    """Search for research papers on arXiv based on the query."""

async def arxiv_search_node(state: AgentState, config: RunnableConfig):
    """
    Arxiv Search Node
    """
    ai_message = cast(AIMessage, state["messages"][-1])

    if ai_message.tool_calls:
        query = ai_message.tool_calls[0]["args"].get("query", "")
        search = arxiv.Search(
            query=query,
            max_results=5,
            sort_by=arxiv.SortCriterion.Relevance
        )
        results = []
        for result in search.results():
            results.append({
                "title": result.title,
                "url": result.entry_id,
                "description": result.summary
            })
        state["resources"] = state.get("resources", []) + results

        return {
            "resources": state["resources"],
            "messages": [ai_message, ToolMessage(
                tool_call_id=ai_message.tool_calls[0]["id"],
                content=f"Arxiv search results: {results}"
            )]
        }

    return {"messages": ai_message}

# coagents-research-canvas/agent/research_canvas/chat.py

from typing import List, cast
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import SystemMessage, AIMessage, ToolMessage
from langchain.tools import tool
from copilotkit.langchain import copilotkit_customize_config
from research_canvas.state import AgentState
from research_canvas.model import get_model
from research_canvas.download import get_resource

@tool
def Search(queries: List[str]):
    """A list of one or more search queries to find good resources to support the research."""

@tool
def WriteReport(report: str):
    """Write the research report."""

@tool
def WriteResearchQuestion(research_question: str):
    """Write the research question."""

@tool
def DeleteResources(urls: List[str]):
    """Delete the URLs from the resources."""

@tool
def RAG(query: str):
    """Retrieve relevant documents and generate an answer based on them."""

async def chat_node(state: AgentState, config: RunnableConfig):
    """
    Chat Node
    """
    config = copilotkit_customize_config(
        config,
        emit_intermediate_state=[
            {
                "state_key": "report",
                "tool": "WriteReport",
                "tool_argument": "report",
            },
            {
                "state_key": "research_question",
                "tool": "WriteResearchQuestion",
                "tool_argument": "research_question",
            },
            {
                "state_key": "rag_response",
                "tool": "RAG",
                "tool_argument": "query",
            }
        ],
        emit_tool_calls=["DeleteResources", "RAG"]
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
    ainvoke_kwargs = {}
    if model.__class__.__name__ in ["ChatOpenAI"]:
        ainvoke_kwargs["parallel_tool_calls"] = False

    response = await model.bind_tools(
        [
            Search,
            WriteReport,
            WriteResearchQuestion,
            DeleteResources,
            RAG
        ],
        **ainvoke_kwargs
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

import json
from typing import cast
from research_canvas.state import AgentState
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import ToolMessage, AIMessage

async def delete_node(state: AgentState, config: RunnableConfig):
    """
    Delete Node
    """
    return state

async def perform_delete_node(state: AgentState, config: RunnableConfig):
    """
    Perform Delete Node
    """
    ai_message = cast(AIMessage, state["messages"][-2])
    tool_message = cast(ToolMessage, state["messages"][-1])
    if tool_message.content == "YES":
        if ai_message.tool_calls:
            urls = ai_message.tool_calls[0]["args"]["urls"]
        else:
            parsed_tool_call = json.loads(
                ai_message.additional_kwargs["function_call"]["arguments"]
            )
            urls = parsed_tool_call["urls"]

        state["resources"] = [
            resource for resource in state["resources"] if resource["url"] not in urls
        ]

    return state

# coagents-research-canvas/agent/research_canvas/demo.py


"""
Demo script to run the FastAPI app.
"""

import os
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
import uvicorn
from copilotkit.integrations.fastapi import add_fastapi_endpoint
from copilotkit import CopilotKitSDK, LangGraphAgent
from research_canvas.agent import graph
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from research_canvas.vector_store import get_all_documents_grouped_by_namespace

app = FastAPI()
sdk = CopilotKitSDK(
    agents=[
        LangGraphAgent(
            name="researchAgent",
            description="Research agent.",
            agent=graph,
        ),
    ],
)

add_fastapi_endpoint(app, sdk, "/copilotkit")

# Allow all origins for development. Restrict in production.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/documents")
async def get_documents():
    print("Incoming request to /api/documents")
    try:
        documents = get_all_documents_grouped_by_namespace()
        return JSONResponse(content=documents)
    except Exception as e:
        print(f"Error fetching documents: {e}")
        return JSONResponse(content={"error": "Failed to fetch documents"}, status_code=500)


@app.get("/health")
def health():
    """Health check."""
    return {"status": "ok"}

from fastapi import Request

@app.post("/copilotkit/agents/researchAgent/invoke")
async def invoke_research_agent(request: Request):
    try:
        payload = await request.json()
        question = payload.get("question")
        documents = payload.get("documents", [])

        if not question:
            return JSONResponse(content={"error": "Question is required."}, status_code=400)

        # Implement your research logic here
        # For demonstration, returning a dummy answer
        answer = f"Received question: {question} with documents: {documents}"

        return {"answer": answer}
    except Exception as e:
        print(f"Error in invoke_research_agent: {e}")
        return JSONResponse(content={"error": "Internal Server Error"}, status_code=500)

def main():
    """Run the uvicorn server."""
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("research_canvas.demo:app", host="127.0.0.1", port=port)


# coagents-research-canvas/agent/research_canvas/agents/document_selection.py

from typing import List, cast
from langchain.tools import tool
from research_canvas.state import AgentState
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import ToolMessage, AIMessage, SystemMessage
from research_canvas.model import get_model
from research_canvas.vector_store import get_all_documents_grouped_by_namespace

@tool
def SelectDocuments(document_ids: List[str]):
    """Select documents by their IDs for the research session."""

async def document_selection_node(state: AgentState, config: RunnableConfig):
    """
    Document Selection Node
    """
    # Fetch available documents from Pinecone
    available_documents = get_all_documents_grouped_by_namespace()

    # Flatten the documents into a list with IDs
    documents_with_ids = []
    for namespace, docs in available_documents.items():
        for doc in docs:
            documents_with_ids.append({
                "id": doc['url'],  # Use URL as ID
                "title": doc['title'],
                "description": doc['description'],
                "namespace": namespace
            })

    state["available_documents"] = documents_with_ids

    model = get_model(state)
    response = await model.bind_tools(
        [SelectDocuments],
    ).ainvoke([
        SystemMessage(content="Select relevant documents for your research."),
        *state["messages"]
    ], config)

    ai_message = cast(AIMessage, response)

    if ai_message.tool_calls:
        selected_ids = ai_message.tool_calls[0]["args"].get("document_ids", [])
        selected_docs = [doc for doc in documents_with_ids if doc['id'] in selected_ids]
        state["selected_documents"] = selected_docs
        return {
            "selected_documents": selected_docs,
            "messages": [ai_message, ToolMessage(
                tool_call_id=ai_message.tool_calls[0]["id"],
                content=f"Selected documents: {selected_ids}"
            )]
        }

    return {"messages": response}

# coagents-research-canvas/agent/research_canvas/download.py


"""
This module contains the implementation of the download_node function.
"""

import aiohttp
import html2text
from copilotkit.langchain import copilotkit_emit_state
from langchain_core.runnables import RunnableConfig
from research_canvas.state import AgentState

_RESOURCE_CACHE = {}

def get_resource(url: str):
    """
    Get a resource from the cache.
    """
    return _RESOURCE_CACHE.get(url, "")

_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/58.0.3029.110 Safari/537.3"
)

async def _download_resource(url: str):
    """
    Download a resource from the internet asynchronously.
    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url,
                headers={"User-Agent": _USER_AGENT},
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                response.raise_for_status()
                html_content = await response.text()
                markdown_content = html2text.html2text(html_content)
                _RESOURCE_CACHE[url] = markdown_content
                return markdown_content
    except Exception as e:
        _RESOURCE_CACHE[url] = "ERROR"
        return f"Error downloading resource: {e}"

async def download_node(state: AgentState, config: RunnableConfig):
    """
    Download resources from the internet.
    """
    state["resources"] = state.get("resources", [])
    state["logs"] = state.get("logs", [])
    resources_to_download = []

    logs_offset = len(state["logs"])

    # Find resources that are not downloaded
    for resource in state["resources"]:
        if not get_resource(resource["url"]):
            resources_to_download.append(resource)
            state["logs"].append({
                "message": f"Downloading {resource['url']}",
                "done": False
            })

    # Emit the state to let the UI update
    await copilotkit_emit_state(config, state)

    # Download the resources
    for i, resource in enumerate(resources_to_download):
        await _download_resource(resource["url"])
        state["logs"][logs_offset + i]["done"] = True

        # Update UI
        await copilotkit_emit_state(config, state)

    return state

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
    if model == "google_genai":
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(
            temperature=0,
            model="gemini-1.5-pro",
            api_key=cast(Any, os.getenv("GOOGLE_API_KEY")) or None
        )

    raise ValueError("Invalid model specified")
import os
from pinecone import Pinecone, ServerlessSpec

# Set up Pinecone API key and environment
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENV = os.getenv("PINECONE_ENVIRONMENT")

# Initialize the Pinecone client
pc = Pinecone(api_key=PINECONE_API_KEY)

# Define the index name and check if it exists
INDEX_NAME = "sample-movies"

# Create a new index if it doesn't exist
if INDEX_NAME not in pc.list_indexes().names():
    pc.create_index(
        name=INDEX_NAME,
        dimension=768,
        metric='cosine', 
        spec=ServerlessSpec(cloud="aws", region=PINECONE_ENV)
    )

# Connect to the index
index = pc.Index(INDEX_NAME)
# coagents-research-canvas/agent/research_canvas/agents/rag_agent.py

from typing import List, cast
from langchain.tools import tool
from research_canvas.state import AgentState
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import AIMessage, ToolMessage, SystemMessage
from research_canvas.vector_store import query_documents
from research_canvas.model import get_model

@tool
def RAG(query: str):
    """Retrieve relevant documents and generate an answer based on them."""

async def rag_node(state: AgentState, config: RunnableConfig):
    """
    Retrieval-Augmented Generation (RAG) Node
    """
    ai_message = cast(AIMessage, state["messages"][-1])

    if ai_message.tool_calls:
        user_query = ai_message.tool_calls[0]["args"].get("query", "")
        namespace = ai_message.tool_calls[0]["args"].get("namespace", None)
        retrieved_docs = query_documents(user_query, top_k=5, namespace=namespace)
        state["retrieved_docs"] = retrieved_docs

        # Generate an answer using the retrieved documents
        model = get_model(state)
        context = "\n\n".join([doc.get('content', '') for doc in retrieved_docs])
        response = await model.ainvoke([
            SystemMessage(content=f"Use the following context to answer the question:\n\n{context}"),
            AIMessage(content=user_query)
        ], config)

        # Add the AI's answer to the state
        state["messages"].append(response)

        return state

    return {"messages": ai_message}
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


from typing import List, TypedDict
from langgraph.graph import MessagesState

class Resource(TypedDict):
    """
    Represents a resource. Give it a good title and a short description.
    """
    url: str
    title: str
    description: str
    namespace: str

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
    available_documents: List[Resource]
    selected_documents: List[Resource]
    retrieved_docs: List[Resource]
# coagents-research-canvas/agent/research_canvas/state.py


from typing import List, TypedDict
from langgraph.graph import MessagesState

class Resource(TypedDict):
    """
    Represents a resource. Give it a good title and a short description.
    """
    url: str
    title: str
    description: str
    namespace: str

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
    available_documents: List[Resource]
    selected_documents: List[Resource]
    retrieved_docs: List[Resource]
# coagents-research-canvas/agent/research_canvas/vector_store.py



import uuid
from research_canvas.pinecone_setup import index
from langchain_openai import OpenAIEmbeddings


OPENAI_API_KEY = "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"

embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)

def query_documents(query, top_k=5, namespace=None):
    embedding = embeddings.embed_text(query)
    result = index.query(
        vector=embedding,
        top_k=top_k,
        include_metadata=True,
        namespace=namespace
    )
    return [match.metadata for match in result.matches]

def get_all_documents_grouped_by_namespace():
    index_stats = index.describe_index_stats()
    index_dimension = index_stats['dimension']
    namespaces = index_stats['namespaces'].keys()
    grouped_documents = {}
    # print("namespaces", namespaces)

    for namespace in namespaces:
        # Use the correct index dimension
        dummy_vector = [0.0] * index_dimension

        result = index.query(
            vector=dummy_vector,
            top_k=100,  # Increase if you have more documents
            include_metadata=True,
            namespace=namespace
        )

        documents = [
            {
                'id': match.id,
                'title': match.metadata.get('title', ''),
                'description': match.metadata.get('summary', ''), 
                'namespace': namespace
            }
            for match in result.matches
            if match.metadata.get('title', '')
        ]
        # print("documents:", documents)
        if documents:
            grouped_documents[namespace] = documents

    return grouped_documents
