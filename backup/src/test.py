from config import load_books
from script import process_book_summary, query_pinecone
books = load_books()


if __name__=="__main__":
    # from IPython import embed
    
    for book in books:
        # Loading books
        
        print("CHECK-> books_details: ", book)
        process_book_summary(book)
        print("CHECK-> done")
        # Set id
        