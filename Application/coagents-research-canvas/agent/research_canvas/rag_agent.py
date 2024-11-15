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
