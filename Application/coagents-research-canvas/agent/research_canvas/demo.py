# coagents-research-canvas/agent/research_canvas/demo.py

"""
Demo script to run the FastAPI app.
"""

import os
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Request
import uvicorn
from copilotkit.integrations.fastapi import add_fastapi_endpoint
from copilotkit import CopilotKitSDK, LangGraphAgent
from research_canvas.agent import graph
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from research_canvas.vector_store import get_all_documents_grouped_by_namespace

app = FastAPI()

# Initialize CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

if __name__ == "__main__":
    main()
