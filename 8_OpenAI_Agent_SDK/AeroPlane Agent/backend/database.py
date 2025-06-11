import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

# Get URI from environment
mongo_uri = os.getenv("Mongo_DB_Connection_String")

# Connect to MongoDB Atlas
client = MongoClient(mongo_uri)

# Choose DB and collection
db = client.airline_db  # This is the database name; it will be created if it doesn't exist
messages_collection = db.messages

# Use regular sync function since pymongo is not async
def store_user_message(user_id: str, message: str, response: str):
    print(f"📦 Storing to DB: {user_id} - {message}")
    messages_collection.insert_one({
        "user_id": user_id,
        "message": message,
        "response": response
    })
