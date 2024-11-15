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

