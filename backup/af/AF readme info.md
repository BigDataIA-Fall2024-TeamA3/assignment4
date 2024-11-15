Part 1: Document Parsing, Vector Storage, and Pipeline Setup


## Overview

Part 1 aims to automate the process of document parsing, vector storage, and pipeline setup using Airflow, Docling, and Pinecone. The project involves parsing documents, storing parsed document vectors in Pinecone for fast and scalable similarity search, and automating the entire process using an Airflow pipeline.

## Table of Contents

- [Overview](#overview)
- [Project Structure](#project-structure)
- [Components and Services](#components-and-services)
- [Setup Instructions](#setup-instructions)
- [Usage](#usage)
- [POC Approaches](#poc-approaches)
- [Important Code Parts](#important-code-parts)

## Components and Services

### Airflow
Airflow is used to automate the document parsing and vector storage process. It schedules and manages the execution of tasks defined in the DAG (Directed Acyclic Graph).

### Docling
Docling is used for parsing documents. It processes the provided dataset, extracts text, and exports structured information.

### Pinecone
Pinecone is used for storing parsed document vectors. It provides fast and scalable similarity search capabilities.

### AWS S3
AWS S3 is used for storing parsed documents and images.

## Setup Instructions

### Prerequisites

- Docker
- Python 3.8
- AWS account with S3 access

### Steps

1. **Clone the Repository**

```bash
   git clone <repository-url>
   cd <repository-directory>
```
2. ENV file
```
SAMPLE_DATA_PATH=path/to/sample_data
SAMPLE_DATA_INFO_PATH=path/to/sample_data_info.json
PINECONE_API_KEY=your_pinecone_api_key
OUTPUT_PATH=path/to/output
SRC_PATH=path/to/src
MODELS_DATA_PATH=path/to/models_data
OPENAI_API_KEY=your_openai_api_key
```

3. Docker image
```
docker build -t airflow-dag .
```

4. Running the container
```
docker run -d -p 8080:8080 --name airflow-container airflow-dag
```

5. Airflow UI at http://localhost:8080 and with username:admin, password:admin

# Other info
## Usage: 
```
Usage
Upload Documents

Place your documents in the src/input folder.

Trigger the DAG

In the Airflow web interface, trigger the docling_pinecone_pipeline DAG manually or wait for the scheduled interval.

Monitor the Pipeline

Monitor the progress of the tasks in the Airflow web interface.

POC Approaches
Document Parsing
Use Docling to parse documents and extract structured information.
Store parsed documents and images in AWS S3.
Vector Storage
Generate vectors from parsed document content.
Store vectors in Pinecone for fast and scalable similarity search.
Pipeline Automation
Build an Airflow pipeline to automate the document parsing and vector storage process.
Schedule and manage the execution of tasks using Airflow.
```
## important functions
```
Important Code Parts
script.py
process_book_summary: Function to process book summaries.
upload_parsed_documents_to_s3: Function to upload parsed documents to S3.
s3_client.py
upload_file: Function to upload files to S3.
list_buckets: Function to list S3 buckets.
list_objects: Function to list objects in an S3 bucket.
books.py
Book class: Represents a book with attributes like title, uuid4, s3_path, etc.
load_books: Function to load books from a JSON file.

dag.py
Defines the Airflow DAG for the pipeline.
Tasks to load books and process each book.
Dockerfile
Sets up the Airflow environment.
Installs necessary Python packages.
Initializes the Airflow database and creates an admin user.
```



# Book attributes
    #     "id": 1,
    #     "title": "handbook of artificial intelligence and big data applications in investments",
    #     "uuid4": "7a55513f-bca7-4d2e-9d65-1b4416d21ea4",
    #     "s3_path": "",
    #     "s3_images_desc_url": "",
    #     "s3_images_folder": "",
    #     "s3_images": [],
    #      "img_desc": [],
    #    "pinecone_index": "7a55513f-bca7-4d2e-9d65-1b4416d21ea4",
    #    "local_output_folder": 
    #     "local_file_path": "./sample_data/7a55513f-bca7-4d2e-9d65-1b4416d21ea4.pdf",
    #     "summary": "This book provides a comprehensive overview of the latest advances in the field of artificial intelligence and big data, focusing on the applications of these technologies in the investment industry."
    # }
```


```
# Code instructions
1. Iterate through a list called pdf_paths,
2. For every path listed, first create a book instance of Book class 
    1. fill in the "title" attribute with the filename after stripping the file path
    2. generate a uuid4 and update the "uuid4" attribute for the book instance
    3. store a copy of the book in the "src/input" folder after renaming it "<uuid4>.pdf" and update "local_file_path" attribute with this information
    4. Generate output folder in "src/output/" called "<uuid4>/" and store this path in "local_output_folder" attribute
    5. Parse <uuid4>.pdf through the docling (store converted markdown_file under "<uuid4>.md" name and images in the output folder)
        1. For every image added to folder, append the "image_file_name" to "s3_images" list attribute of book instance
        2. For every image, ping generate_summary() function in Book class and append the following `{"image_file_name": "description"}` to "img_desc" list attribute of the book instance
    7. Create or overwrite "img_desc.json" in "src/output/<uuid4>/" folder with "img_desc" list attribute information after converting it to json
    8. Upload the following
        1. "<uuid4>.pdf" to damg_pdf_input bucket on s3
        2. "<uuid4>.md" to damg_md_files bucket on s3
        3. rename "img_desc.json" to "<uuid4>.json" and upload to damg_img_desc bucket on s3
        4. create an empty markdown file or overwrite "<uuid4>_research_notes.md" to damg_md_files bucket on s3
    9. Overwrite the updated the Book attribute information to the list of books list stored in "data.json" file at MODELS_DATA_PATH dir
    10. Generate pinecone embeddings
        1. Create pinecone_index with pinecone_index_name called "uuid4" attribute of the book instance
            1. create setup and configure the following
                1. create pinecone_namespaces named ["img", "md", "research_notes"] all under pinecone_index named <uuid4>
                2. the input files for "img" namespace is "img_desc.json"
                3. the input file for "md" namespace is "<uuid4>.md"
                4. The input file for "research_notes" namespace is "<uuid4>_research_notes.md"
            2. Iterate through each namespace and their respective input files,
                1. create preprocessed data by with tiktoken library to chunk the data in the respective input file in the following format `data = [{"id": "vec1", "text": "Apple is a popular fruit known for its sweetness and crisp texture."}, {"id": "vec2", "text": "The tech company Apple is known for its innovative products like the iPhone."},... {"id": <vec_n>, "text": "chunked data"}]`
                2. Generate, upsert and test by querying embeddings (refer and suggest modifications to "save_to_pinecone()" and "query_pinecone()" function in script.py file)
3. Generate a s3_client with boto3 in `s3_client.py` to handle the relevant operations efficiently
4. Generate a pinecone_client in `pinecone_client.py` to handle the relevant functions effeciently            
```
