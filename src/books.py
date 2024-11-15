import json
from config import fastapi_config, mock_data, load_data, load_books

books = load_books()


# s3 buckets = (images, input_files, output_files, research_notes)

class Book():
    def __init__(self, json_data) -> None:
        # Load from dict file
        self.id = json_data["id"]
        self.title = json_data["title"]
        self.uuid4 = json_data["uuid4"]
        self.s3_path = json_data["s3_path"]
        self.s3_images_desc_url = json_data["s3_images_desc_url"]
        self.s3_images_folder = json_data["s3_images_folder"]
        self.s3_images = json_data["s3_images"]
        self.pinecone_index = json_data["pinecone_index"]
        self.local_file_path = json_data["local_file_path"]
        self.summary = json_data["summary"]


    
    
    # def __init__(self) -> None:
    #     self.id = None
    #     self.title = None
    #     self.uuid4 = None
    #     self.s3_path = None
    #     self.s3_images_desc_url = None
    #     self.s3_images_folder = None
    #     self.s3_images = []
    #     self.pinecone_index = self.uuid4
    #     self.local_file_path = None
    #     self.summary = None

    # def load_sample_data(file_path=None):
    # import json
    # if file_path is None:
    #     fastapi_config = Config()
    #     file_path = fastapi_config.SAMPLE_DATA_INFO_PATH
    # try:
    #     with open(file_path, 'r') as file:
    #         return json.load(file)
    # except FileNotFoundError:
    #     print(f"Error: File '{file_path}' not found.")
    #     return {}
    # except json.JSONDecodeError:
    #     print(f"Error: Invalid JSON in '{file_path}'.")
    #     return {}

    
    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "uuid4": self.uuid4,
            "s3_path": self.s3_path,
            "s3_images_desc_url": self.s3_images_desc_url,
            "s3_images_folder": self.s3_images_folder,
            "s3_images": self.s3_images,
            "local_file_path": self.local_file_path,
            "summary": self.summary
        }
    
    
    
    def append_src_data(self):
        with open(fastapi_config.SRC_PATH + "/" + fastapi_config.MODELS_DATA_PATH, 'w') as file:
                books.append(self.to_dict())
                json.dump(books, file, indent=2)
        
    
    
    
    @classmethod
    def from_dict(cls, book_dict):
        return cls(
            id=book_dict["id"],
            title=book_dict["title"],
            uuid4=book_dict["uuid4"],
            s3_path=book_dict["s3_path"],
            s3_images_desc_url=book_dict["s3_images_desc_url"],
            s3_images_folder=book_dict["s3_images_folder"],
            s3_images=book_dict["s3_images"],
            local_file_path=book_dict["local_file_path"],
            summary=book_dict["summary"]
        )

