from pymongo import MongoClient
from datetime import datetime
import os 
from bson import ObjectId
from dotenv import load_dotenv

load_dotenv()

# MongoDB Connection (Replace with your credentials)
MONGO_URI = os.getenv("MONGO_CONNECTION_STRING")
print(MONGO_URI)

client = MongoClient(MONGO_URI)
db = client["GitaBot"]  # Database name
collection = db["chat_history"]  # Collection name

def save_chat(user_id, user_message, bot_response):
    """Save chat history in MongoDB with messages as an array."""
    
    user_id = ObjectId(user_id)  # Ensure user_id is stored correctly as ObjectId
    
    # Prepare message entries
    user_entry = {"role": "user", "text": user_message, "timestamp": datetime.utcnow()}
    bot_entry = {"role": "bot", "text": bot_response, "timestamp": datetime.utcnow()}
    
    # Check if a chat history already exists for the user
    existing_chat = collection.find_one({"user_id": user_id})
    
    if existing_chat:
        # Append new messages to the existing chat history
        collection.update_one(
            {"user_id": user_id},
            {"$push": {"messages": {"$each": [user_entry, bot_entry]}}}
        )
    else:
        # Create a new chat entry for the user
        chat_entry = {
            "user_id": user_id,
            "messages": [user_entry, bot_entry]
        }
        collection.insert_one(chat_entry)

    return {"message": "Chat saved successfully!"}

def get_chat_history(user_id, limit=5):
    """Retrieve last 5 messages of a user."""
    chats = collection.find({"user_id": user_id}).sort("timestamp", -1).limit(limit)
    return [(chat["user_message"], chat["bot_response"]) for chat in chats]
