from pymongo import MongoClient

client = MongoClient('mongodb+srv://satyamiitism_db_user:mOOMP9nvSyXNrPuC@cluster0.swxtgho.mongodb.net/')
filter={}

db_name = "bahlolpur_ancestory"
col_name = "family_members"

FAMILY_COLLECTION  = client[db_name][col_name]
