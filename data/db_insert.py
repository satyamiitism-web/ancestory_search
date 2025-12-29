from pymongo import MongoClient

# 1. Setup Connection
client = MongoClient('mongodb+srv://satyamiitism_db_user:mOOMP9nvSyXNrPuC@cluster0.swxtgho.mongodb.net/')
db = client['bahlolpur_ancestory']
# specific collection for people
collection = db['family_members']

# 2. Your Raw Data (The big dictionary you provided)
raw_data = {
  "_id": {
    "$oid": "69525619903bb8eca96ff92f"
  },
  "satyam anand": {
    "name": "Satyam Anand",
    "gender": "M",
    "spouse": "Golden",
    "parents": [
      "Madhukar Anand",
      "Nilu Sharma"
    ]
  },
  "golden": {
    "name": "Golden",
    "gender": "F",
    "spouse": "Satyam Anand",
    "parents": []
  },
  "shivesh anand": {
    "name": "Shivesh Anand",
    "gender": "F",
    "spouse": "",
    "parents": [
      "Madhukar Anand",
      "Nilu Sharma"
    ]
  },
  "babli kumari": {
    "name": "Babli Kumari",
    "gender": "F",
    "spouse": "",
    "parents": [
      "Pankaj Kumar",
      "Rita Sharma"
    ]
  },
  "amritansh anand": {
    "name": "Amritansh Anand",
    "gender": "M",
    "spouse": "",
    "parents": [
      "Pankaj Kumar",
      "Rita Sharma"
    ]
  },
  "abhinit anand": {
    "name": "Abhinit Anand",
    "gender": "M",
    "spouse": "",
    "parents": [
      "Niraj Kumar",
      "Ragini Kumari"
    ]
  },
  "madhukar anand": {
    "name": "Madhukar Anand",
    "gender": "M",
    "spouse": "Nilu Sharma",
    "parents": [
      "Ramanand Sharma",
      "Indu Devi"
    ]
  },
  "nilu sharma": {
    "name": "Nilu Sharma",
    "gender": "F",
    "spouse": "Madhukar Anand",
    "parents": []
  },
  "pankaj kumar": {
    "name": "Pankaj Kumar",
    "gender": "M",
    "spouse": "Rita Sharma",
    "parents": [
      "Ramanand Sharma",
      "Indu Devi"
    ]
  },
  "rita sharma": {
    "name": "Rita Sharma",
    "gender": "F",
    "spouse": "Pankaj Kumar",
    "parents": []
  },
  "niraj kumar": {
    "name": "Niraj Kumar",
    "gender": "M",
    "spouse": "Ragini Kumari",
    "parents": [
      "Ramanand Sharma",
      "Indu Devi"
    ]
  },
  "ragini kumari": {
    "name": "Ragini Kumari",
    "gender": "F",
    "spouse": "Niraj Kumar",
    "parents": []
  },
  "ramanand sharma": {
    "name": "Ramanand Sharma",
    "gender": "M",
    "spouse": "Indu Devi",
    "parents": [
      "Bangali Sharma",
      "Dash Devi"
    ]
  },
  "indu devi": {
    "name": "Indu Devi",
    "gender": "F",
    "spouse": "Ramanand Sharma",
    "parents": []
  },
  "bangali sharma": {
    "name": "Bangali Sharma",
    "gender": "M",
    "spouse": "Dash Devi",
    "parents": []
  },
  "dash devi": {
    "name": "Dash Devi",
    "gender": "F",
    "spouse": "Bangali Sharma",
    "parents": []
  }
}

# 3. Transform and Insert
new_documents = []

for key, person_data in raw_data.items():
    # Skip the mongo _id if it exists in the raw data
    if key == "_id":
        continue
    # Create a clean document
    doc = {
        # Store the lowercase key as a 'slug' for fast, reliable lookup
        "slug": key,
        "name": person_data['name'],
        "gender": person_data['gender'],
        "spouse": person_data['spouse'],
        "parents": person_data['parents']
    }
    new_documents.append(doc)

if new_documents:
    collection.drop()  # Clear old testing data if needed
    collection.insert_many(new_documents)
    
    # CRITICAL: Create an index on the 'slug' and 'name' for speed
    collection.create_index("slug", unique=True)
    collection.create_index("parents")
    
    print(f"Successfully migrated {len(new_documents)} people.")
