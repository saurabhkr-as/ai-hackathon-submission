import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
db=client["ai-hackathon"]
collection=db["call_detail"]



async def save_to_db(data):
    try:
        print("Saving to DB:")
        data=data.dict()
        collection.insert_one(data)
        print("Data saved successfully")
    except Exception as e:
        print(f"Error saving to DB: {e}")

