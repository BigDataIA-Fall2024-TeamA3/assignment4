import csv
import json
from IPython import embed
# Read the CSV file
books = []
count = 0
with open('src/input.csv', mode='r', encoding='utf-8') as csv_file:
    csv_reader = csv.DictReader(csv_file, fieldnames=("TITLE", "SUMMARY", "PDF_LINK", "IMAGE_LINK", "ROW_NUM"))
    # embed()
    for row in csv_reader:
        count+=1
        book = {
            "id": int(count),
            "title": row["TITLE"],
            "uuid4": "",  # Generate or assign UUID if needed
            "s3_path": row["PDF_LINK"],
            "s3_frontpage_url": row["IMAGE_LINK"],
            "s3_images_desc_url": "",
            "s3_images_folder": "",  # Assign if needed
            "s3_images": [],  # Assign if needed
            "local_file_path": "",  # Assign if needed
            "pinecone_index": "",  # Assign if needed
            "summary": row["SUMMARY"]
        }
        books.append(book)

# Write to JSON file
data = {"books": books}
with open('src/data.json', mode='w', encoding='utf-8') as json_file:
    json.dump(data, json_file, indent=4)