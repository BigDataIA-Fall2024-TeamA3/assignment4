# - [ ] Pipeline Automation: Build an Airflow pipeline that integrates Docling and Pinecone to automate the document parsing and vector storage process.

from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
from script import process_book_summary, load_books

# Default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Define the DAG
dag = DAG(
    'docling_pinecone_pipeline',
    default_args=default_args,
    description='A pipeline that integrates Docling and Pinecone to automate document parsing and vector storage',
    schedule_interval=timedelta(days=1),
)

# Task to load books
def load_books_task():
    books = load_books()
    return books

# Task to process each book
def process_book_task(book):
    process_book_summary(book)

# Task to iterate through books and process them
def process_all_books_task():
    books = load_books_task()
    for book in books:
        process_book_task(book)

# Define the tasks
load_books_operator = PythonOperator(
    task_id='load_books',
    python_callable=load_books_task,
    dag=dag,
)

process_books_operator = PythonOperator(
    task_id='process_books',
    python_callable=process_all_books_task,
    dag=dag,
)

# Set the task dependencies
load_books_operator >> process_books_operator

# Add comments to explain the purpose of each task
"""
Task: load_books
Purpose: Load the list of books from the data source.

Task: process_books
Purpose: Iterate through the list of books and process each book by parsing the document, uploading parsed documents to S3, generating vectors, and saving them to Pinecone.
"""

if __name__ == "__main__":
    dag.cli()