Assignment 4 Fall 2024
Objective
Build an end-to-end research tool using an Airflow pipeline to process documents, store
and search vectors, and create a multi-agent research interface.
Requirements
Part 1: Document Parsing, Vector Storage, and Pipeline Setup
1. Airflow Pipeline
○ Document Parsing: Use Docling for parsing documents. Configure Docling
to process the provided dataset, extract text, and export structured
information.
○ Vector Storage with Pinecone: Store the parsed document vectors in
Pinecone for fast and scalable similarity search.
○ Pipeline Automation: Build an Airflow pipeline that integrates Docling
and Pinecone to automate the document parsing and vector storage
process.
Part 2: Research Agent with Pinecone and Langraph
1. Agent Setup
○ Use Pinecone for vector storage and retrieval.
○ Use Langraph to create a multi-agent system for document-based
research. The system should allow:
■ Document Selection: Offer only the documents processed in Part1 for research.
■ Arxiv Agent: Search relevant research papers.
■ Web Search Agent: Conduct online research for broader context.
■ RAG (Retrieval-Augmented Generation) Agent: Answer queries
based on document content using Pinecone and Langraph.
Part 3: Research Interface and Q/A Interaction
1. User Interaction Interface
○ Choose Coagents to create a user interface for conducting research:
■ Allow users to ask 5-6 questions per document.
■ Save results of each research session.
2. Export Results
○ Professional PDF Report: Export research findings in a templated,
professional PDF file.
○ Codelabs: Structure findings in a Codelabs format for instructional clarity
and future reference.
Submission Requirements
1. GitHub Repository
○ Project summary, proof of concept (PoC), and a detailed issue tracker.
○ Diagrams, a fully documented Codelab, and a 5-minute solution video.
○ Links to hosted application and backend services.
2. Documentation
○ README.md file with instructions for setup, usage, and access.
○ Comprehensive guide for interacting with deployed applications