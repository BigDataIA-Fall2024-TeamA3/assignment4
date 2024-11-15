# coagents-research-canvas/agent/research_canvas/vector_store.py



import uuid
import os
from research_canvas.pinecone_setup import index
from langchain_openai import OpenAIEmbeddings


OPENAI_API_KEY =  os.getenv("OPENAI_API_KEY")

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
