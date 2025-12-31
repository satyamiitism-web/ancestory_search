from pymongo import MongoClient
from dotenv import load_dotenv
import os
load_dotenv('.env')

MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(MONGO_URI)
filter={}

db_name = "bahlolpur_ancestory"
col_name = "family_members"

FAMILY_COLLECTION  = client[db_name][col_name]
USERS_COLLECTION = client[db_name]["users"]
