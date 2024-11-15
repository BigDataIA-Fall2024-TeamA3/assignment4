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

