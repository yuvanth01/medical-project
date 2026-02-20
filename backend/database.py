from pymongo import MongoClient
client = MongoClient("mongodb://localhost:27017")
db = client["medical_db"]
collection = db["bills"]