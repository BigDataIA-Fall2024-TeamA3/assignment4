import os
from dotenv import load_dotenv
# from IPython import embed
load_dotenv()

class Config:
    
    AWS_ACCESS_KEY_ID=os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY=os.getenv('AWS_SECRET_ACCESS_KEY')
    AWS_REGION=os.getenv('AWS_REGION')
    S3_BUCKET_NAME=os.getenv('S3_BUCKET_NAME')
    # NVIDIA_API_KEY=os.getenv('NVIDIA_API_KEY')
    # SNOWFLAKE_ACCOUNT=os.getenv('SNOWFLAKE_ACCOUNT')
    # SNOWFLAKE_USER=os.getenv('SNOWFLAKE_USER')
    # SNOWFLAKE_PASSWORD=os.getenv('SNOWFLAKE_PASSWORD')
    # SNOWFLAKE_WAREHOUSE=os.getenv('SNOWFLAKE_WAREHOUSE')
    # SNOWFLAKE_DATABASE=os.getenv('SNOWFLAKE_DATABASE')
    # SNOWFLAKE_SCHEMA=os.getenv('SNOWFLAKE_SCHEMA')
    # SNOWFLAKE_ROLE=os.getenv('SNOWFLAKE_ROLE')
    # ZILLIZ_CLOUD_URI = os.getenv('ZILLIZ_CLOUD_URI')
    # ZILLIZ_CLOUD_API_KEY = os.getenv('ZILLIZ_CLOUD_API_KEY')
    SAMPLE_DATA_PATH = os.getenv('SAMPLE_DATA_PATH')
    SAMPLE_DATA_INFO_PATH = os.getenv('SAMPLE_DATA_INFO_PATH')
    PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
    OUTPUT_PATH = os.getenv('OUTPUT_PATH')
    SRC_PATH = os.getenv('SRC_PATH')
    MODELS_DATA_PATH = os.getenv('MODELS_DATA_PATH')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

def load_sample_data(file_path=None):
    import json
    if file_path is None:
        fastapi_config = Config()
        file_path = fastapi_config.SAMPLE_DATA_INFO_PATH
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return {}
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in '{file_path}'.")
        return {}
    
# # At the top of your main script
fastapi_config = Config()
mock_data = load_sample_data()

def load_data(file_path=None):
    import json
    import os
    if file_path is None:
        fastapi_config = Config()
        file_path = fastapi_config.SRC_PATH + "/" + fastapi_config.MODELS_DATA_PATH
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return {}
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in '{file_path}'.")
        return {}

def load_books(file_path=None):
    if file_path is None:
        x = load_data()
        return x["books"]
    
pdf_booklist = load_books()
    


# # Now you can use mock_data throughout your application
# users = mock_data.get('users', [])
# products = mock_data.get('products', [])

# # Rest of your application code...

# def save_mock_data(data, file_path='mock_data.json'):
#     with open(file_path, 'w') as file:
#         json.dump(data, file, indent=2)

# Usage
# mock_data['users'].append({"id": 3, "name": "New User", "email": "new@example.com"})
# save_mock_data(mock_data)
