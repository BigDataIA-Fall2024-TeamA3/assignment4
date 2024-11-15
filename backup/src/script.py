#  1. Airflow Pipeline
# - [x] Document Parsing: Use Docling for parsing documents. Configure Docling to process the provided dataset, extract text, and export structured information.
# - [x] Vector Storage with Pinecone: Store the parsed document vectors in Pinecone for fast and scalable similarity search.
# - [in progress] Pipeline Automation: Build an Airflow pipeline that integrates Docling and Pinecone to automate the document parsing and vector storage process.


# from IPython import embed
from config import fastapi_config, mock_data, load_data, load_books
from books import Book


from IPython import embed

from docling.document_converter import DocumentConverter

import logging
import time
from pathlib import Path

from docling_core.types.doc import ImageRefMode, PictureItem, TableItem

from docling.datamodel.base_models import FigureElement, InputFormat, Table
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption

_log = logging.getLogger(__name__)

IMAGE_RESOLUTION_SCALE = 2.0
DUMMY_IMG_PATH = "https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/15b17bf0-fb1a-4fb2-b952-beee07706068/original=true/00088-3178799381.jpeg"
books = load_books()

# Generate description for an image
def generate_image_desc(image_url = DUMMY_IMG_PATH):
    import os
    import uuid, datetime
    import requests
    # from IPython.display import Image
    from langchain_core.messages import HumanMessage
    from langchain_openai import ChatOpenAI

    uid = uuid.uuid4().hex[:6]
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    project_name = "img_summarizer_{current_time}_{uid}"
    os.environ["LANGCHAIN_TRACING_V2"]="true"
    os.environ["LANGCHAIN_PROJECT"]=project_name
    
    # Summary Prompt
    summary_prompt_text = """What's in this image?"""

    # Analysis Prompt
    analysis_prompt_text = """Please provide bullet point summaries for the image in each of the following categories:
    - Medium: 
    - Subject: 
    - Scene: 
    - Style: 
    - Artistic Influence or Movement: 
    - Website: 
    - Color: 
    - Lighting:
    - Additional Details: 

    If you don't know the answer for one of the categories, leave it blank."""
    
    # Create a human message
    def ask_message(prompt, image_url):
        chat = ChatOpenAI(model="gpt-4-vision-preview", max_tokens=1024)
        msg = chat.invoke(
            [
                HumanMessage(
                    content=[
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {"url": image_url},
                        },
                    ]
                )
            ]
        )
        return msg.content
    
    # Generate summary
    summary = ask_message(summary_prompt_text, image_url)
    analysis = ask_message(analysis_prompt_text, image_url)
    
    return {
        "img_url": image_url,
        "summary": summary,
        "analysis": analysis
    }
        
    
        
    
    
# books = load_books()
# for book_data in books:
#     book = Book(book_data)
#     upload_parsed_documents_to_s3(book)

# Page.text is not working -> FIX IT
def process_book_summary(book_data):
    book = Book(book_data)
    
    # Parse document content
    book, data = parse_documents(book)
    # Upload parsed documents to S3
    book = upload_parsed_documents_to_s3(book)
    # Generate embeddings for parsed data and upsert the vectors to pinecone index\
    index_book(book)
    
    
    # Update the book instance with the relevant details
    
    # sample query
    # query_pinecone("Tell me about apple")
    
    # Sample delete the index
    # delete_pinecone_index()
    
    
    
    pass
# write a function to upload the parsed documents to s3

def upload_parsed_documents_to_s3(book=None):
    import json
    from pathlib import Path
    from s3_client import upload_file
    from books import Book, load_books
    if book is None:
        return ''
    
    # Define the S3 bucket name and the folder path
    bucket_name = 'mya4bucket'
    folder_path = f"{bucket_name}/{book.uuid4}"
    
    # Get the output directory from the parsed documents
    output_dir = Path(fastapi_config.OUTPUT_PATH) / book.uuid4
    
    # Upload all files in the output directory to S3
    for file_path in output_dir.glob('*'):
        upload_file(str(file_path), bucket_name)
    
    # Update the book instance attributes
    book.s3_path = f"https://{bucket_name}.s3.amazonaws.com/{folder_path}/{book.uuid4}.pdf"
    book.s3_images_folder = f"https://{bucket_name}.s3.amazonaws.com/{folder_path}/images/"
    
    # Update data.json with the updated book instance info
    books = load_books()
    for i, b in enumerate(books):
        if b['id'] == book.id:
            books[i] = book.to_dict()
            break
    
    with open('data.json', 'w') as json_file:
        json.dump({"books": books}, json_file, indent=4)
    
    return book

def parse_documents(book=None):
    # old_structure_data_info
    input_doc_path = Path(book.local_file_path)
    print(input_doc_path)
    output_dir = Path(fastapi_config.OUTPUT_PATH + '/' + book.uuid4)
    converter = DocumentConverter()
    result = converter.convert(input_doc_path)
    # print(result.document.export_to_markdown())

    # Save markdown with embedded pictures
    content_md = result.document.export_to_markdown()
    doc_filename = result.input.file.stem
    md_filename = output_dir / f"{doc_filename}-with-images.md"
    
    with md_filename.open("w") as fp:
        fp.write(content_md)
    
    
    
    return book, {
        "document": doc_filename,
        "pages": len(result.document.pages),
        "markdown_file": md_filename,
        "output_dir": output_dir,
    }
    
    
def parse_document(book=None):
# def parse_documents(input_path, output_path):
    
    logging.basicConfig(level=logging.INFO)

    input_doc_path = Path(book.local_file_path)
    print(input_doc_path)
    output_dir = Path(fastapi_config.OUTPUT_PATH + '/' + book.uuid4)
    image_desc = []


    # Important: For operating with page images, we must keep them, otherwise the DocumentConverter
    # will destroy them for cleaning up memory.
    # This is done by setting PdfPipelineOptions.images_scale, which also defines the scale of images.
    # scale=1 correspond of a standard 72 DPI image
    # The PdfPipelineOptions.generate_* are the selectors for the document elements which will be enriched
    # with the image field
    pipeline_options = PdfPipelineOptions()
    pipeline_options.images_scale = IMAGE_RESOLUTION_SCALE
    pipeline_options.generate_page_images = True
    pipeline_options.generate_table_images = True
    pipeline_options.generate_picture_images = True

    doc_converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
        }
    )

    start_time = time.time()
    conv_res = doc_converter.convert(input_doc_path)

    output_dir.mkdir(parents=True, exist_ok=True)
    doc_filename = conv_res.input.file.stem

    # Save page images
    for page_no, page in conv_res.document.pages.items():
        page_no = page.page_no
        page_image_filename = output_dir / f"{doc_filename}-{page_no}.png"
        with page_image_filename.open("wb") as fp:
            page.image.pil_image.save(fp, format="PNG")

    # Save images of figures and tables
    table_counter = 0
    picture_counter = 0
    for element, _level in conv_res.document.iterate_items():
        if isinstance(element, TableItem):
            table_counter += 1
            element_image_filename = (
                output_dir / f"{doc_filename}-table-{table_counter}.png"
            )
            with element_image_filename.open("wb") as fp:
                element.image.pil_image.save(fp, "PNG")

            table_desc = generate_image_desc(element_image_filename)
            print("CHECK-> table_desc: ", table_desc)
            image_desc.append({f"{doc_filename}-table-{table_counter}": table_desc})
                
        if isinstance(element, PictureItem):
            picture_counter += 1
            element_image_filename = (
                output_dir / f"{doc_filename}-picture-{picture_counter}.png"
            )
            with element_image_filename.open("wb") as fp:
                element.image.pil_image.save(fp, "PNG")
        
            # Upload to s3 and generate the image_summary
            
            table_desc = generate_image_desc(element_image_filename)
            print("CHECK-> image_desc: ", table_desc)
            image_desc.append({f"{doc_filename}-picture-{picture_counter}": table_desc})


    # Save markdown with embedded pictures
    content_md = conv_res.document.export_to_markdown(image_mode=ImageRefMode.EMBEDDED)
    md_filename = output_dir / f"{doc_filename}-with-images.md"
    with md_filename.open("w") as fp:
        fp.write(content_md)
    
    with open(output_dir / f"{doc_filename}-image-desc.json", "w") as fp:
        import json
        json.dump(image_desc, fp, indent=4)

    end_time = time.time() - start_time

    _log.info(f"Document converted and figures exported in {end_time:.2f} seconds.")
    # old_structure_data_info
    # return {
    #     "document": doc_filename,
    #     "pages": len(conv_res.document.pages),
    #     "tables": table_counter,
    #     "pictures": picture_counter,
    #     "markdown_file": md_filename,
    #     "output_dir": output_dir,
    # }
        
    
    return book, {
        "document": doc_filename,
        "pages": [
            {
                "number": page_no,
                "content": page.text,
                "image_path": str(output_dir / f"{doc_filename}-{page_no}.png")
            } for page_no, page in conv_res.document.pages.items()
        ],
        "tables": [
            {
                "number": i+1,
                "content": table.text,
                "image_path": str(output_dir / f"{doc_filename}-table-{i+1}.png")
            } for i, table in enumerate(conv_res.document.tables)
        ],
        "pictures": [
            {
                "number": i+1,
                "image_path": str(output_dir / f"{doc_filename}-picture-{i+1}.png")
            } for i, picture in enumerate(conv_res.document.pictures)
        ],
        "markdown_file": str(md_filename),
        "output_dir": str(output_dir),
    }

# Pinecone function
try:
    from pinecone.grpc import PineconeGRPC as Pinecone
except ImportError:
    from pinecone import Pinecone
from pinecone import ServerlessSpec

def delete_pinecone_index(pinecone_index_name="example-index"):
    pc = Pinecone(api_key=fastapi_config.PINECONE_API_KEY)
    pc.delete_index(pinecone_index_name)

def query_pinecone(query="Tell me about apple", pinecone_index_name="example-index", pinecone_namespace='example-namespace'):
    pc = Pinecone(api_key=fastapi_config.PINECONE_API_KEY)
    index = pc.Index(pinecone_index_name)
    # Convert the query into a numerical vector that Pinecone can search with
    query_embedding = pc.inference.embed(
        model="multilingual-e5-large",
        inputs=[query],
        parameters={
            "input_type": "query"
        }
    )

    # Search the index for the three most similar vectors
    results = index.query(
        namespace=pinecone_namespace,
        vector=query_embedding[0].values,
        top_k=3,
        include_values=False,
        include_metadata=True
    )

    print(results)
    return

def chunk_data_into_pages(md_filename):
    # Load the markdown content
    import tiktoken
    data = tiktoken.load_markdown(md_filename)
    
    # Initialize parsed_data
    parsed_data = {
        "pages": []
    }
    
    # Define the chunk size (number of tokens per page)
    chunk_size = 1000  # Adjust this value as needed
    
    # Split the data into chunks
    chunks = [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]
    
    # Load the chunks into parsed_data
    for i, chunk in enumerate(chunks):
        page = {
            "number": i + 1,
            "content": chunk
        }
        parsed_data["pages"].append(page)
    
    return parsed_data

def generate_vectors(book=None):
    pc = Pinecone(api_key=fastapi_config.PINECONE_API_KEY)
    vectors = []
    output_dir = ""
    if book is not None:
        output_dir = Path(fastapi_config.OUTPUT_PATH + '/' + book.uuid4)
        md_filename = output_dir / f"{book.uuid4}-with-images.md"
    
    parsed_data = chunk_data_into_pages(md_filename)
    # can you write to chunk the data into pages and load them into parsed_data
    # print("CHECK-> page: ", page)
    # print("CHECK-> page['content']: ", page['content'])
    # print("CHECK-> page['number']: ", page['number'])
    
    for page in parsed_data['pages']:
        print("CHECK-> page: ", page)
        print("CHECK-> page['content']: ", page['content'])
        print("CHECK-> page['number']: ", page['number'])
        
        embeddings = pc.inference.embed(
            model="multilingual-e5-large",
            inputs=[page['content']],
            parameters={"input_type": "passage", "truncate": "END"}
        )
        
        vectors.append({
            "id": f"page_{page['number']}",
            "values": embeddings[0]['values'],
            "metadata": {
                "type": "page",
                "number": page['number'],
                "image_path": page['image_path']
            }
        })
        print("save_to_pinecone CHECK-> embeddings: ", embeddings)
        return vectors
        
def save_vectors_to_pinecone_index(vectors=[], pinecone_index_name="example-index", pinecone_namespace="research"):
    pc = Pinecone(api_key=fastapi_config.PINECONE_API_KEY)
    if not pc.has_index(pinecone_index_name):
        pc.create_index(
            name=pinecone_index_name,
            dimension=1024,
            metric="cosine",
            spec=ServerlessSpec(
                cloud='aws', 
                region='us-east-1'
            ) 
        ) 

    # Wait for the index to be ready
    while not pc.describe_index(pinecone_index_name).status['ready']:
        time.sleep(1)
        print("save_vectors_to_pinecone_index CHECK-> pinecone_index_name: "+pinecone_index_name+": Waiting for the index to be ready...")
    
    print("save_vectors_to_pinecone_index CHECK-> pinecone_index_name: "+pinecone_index_name+": Index ready!")
    
    # Prepare the records for upsert 
    index = pc.Index(pinecone_index_name)
    # Prepare the records for upsert
    # Each contains an 'id', the embedding 'values', and the original text as 'metadata'

    # Upsert the records into the index
    index.upsert(
        vectors=vectors,
        namespace=pinecone_namespace
    )
    
    while not pc.describe_index(pinecone_index_name).status['ready']:
        time.sleep(1)
        print("save_to_pinecone CHECK-> pinecone_index_name: "+pinecone_index_name+": Waiting for the index (upsert) to be ready...")
    
    print("save_to_pinecone CHECK-> pinecone_index_name: "+pinecone_index_name+": Index (upsert) ready!")
    return index.describe_index_stats()

def index_book(book):
    # parsed_data = parse_document(book)
    vectors = generate_vectors(book)
    save_vectors_to_pinecone_index(vectors, book.uuid4)
    return

if __name__=="__main__":
    # from IPython import embed
    
    for book in books:
        # Loading books
        
        print("CHECK-> books_details: ", book)
        process_book_summary(book)
        print("CHECK-> done")
        # Set id
        
        # print("CHECK-> output_path: ", fastapi_config.OUTPUT_PATH+book["uuid4"])
        # parsed_data = parse_documents(book["local_file_path"], fastapi_config.OUTPUT_PATH + '/' + book["uuid4"])
        # print("CHECK-> parsed_data: ", parsed_data)
        # vectors = generate_vectors(parsed_data)
        # print("CHECK-> vectors", vectors)
        # save_vectors_to_pinecone_index(vectors, book["uuid4"])
        
    # # Testing pinecone
    # delete_pinecone_index()



