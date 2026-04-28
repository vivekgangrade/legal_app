"""
Simple script to check MongoDB collections and their document counts.
"""
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017")
db = client["legal_db"]

print("Collections in legal_db:")
for name in db.list_collection_names():
    count = db[name].count_documents({})
    print(f"  - {name}: {count} documents")
    
    # Show sample document
    sample = db[name].find_one()
    if sample:
        sample.pop("_id", None)
        print(f"    Sample: {sample}")
