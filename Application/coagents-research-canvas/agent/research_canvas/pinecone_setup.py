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
