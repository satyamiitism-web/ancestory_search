from pymongo import MongoClient
from dotenv import load_dotenv
import os
load_dotenv('.env')

MONGO_URI = os.getenv("MONGO_URI")


client = MongoClient(MONGO_URI)
db = client['bahlolpur_ancestory']
collection = db['family_members']

# 3. Transform and Insert
new_documents = []

# for key, person_data in raw_data.items():
#     # Skip the mongo _id if it exists in the raw data
#     if key == "_id":
#         continue
#     # Create a clean document
#     doc = {
#         # Store the lowercase key as a 'slug' for fast, reliable lookup
#         "slug": key,
#         "name": person_data['name'],
#         "gender": person_data['gender'],
#         "spouse": person_data['spouse'],
#         "parents": person_data['parents']
#     }
#     new_documents.append(doc)

# if new_documents:
#     collection.drop()  # Clear old testing data if needed
#     collection.insert_many(new_documents)
    
#     # CRITICAL: Create an index on the 'slug' and 'name' for speed
#     collection.create_index("slug", unique=True)
#     collection.create_index("parents")
    
#     print(f"Successfully migrated {len(new_documents)} people.")
