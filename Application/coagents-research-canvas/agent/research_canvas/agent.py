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

