# db.py
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["med_info_db"]
drug_collection = db["drugs"]

