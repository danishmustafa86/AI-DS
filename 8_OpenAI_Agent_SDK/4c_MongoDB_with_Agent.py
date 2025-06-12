from openai import AsyncOpenAI
from agents import Agent, OpenAIChatCompletionsModel, Runner, function_tool
from datetime import datetime
from dotenv import load_dotenv
import os
from pymongo import MongoClient
from pymongo.server_api import ServerApi

# ✅ Load environment variables from .env file
load_dotenv()

# ✅ Get MongoDB URI from environment
uri = os.getenv('Mongo_DB_Connection_String')
if not uri:
    raise ValueError("❌ Mongo_DB_Connection_String not set in .env file")

# ✅ Connect to MongoDB Atlas
Mongo_client = MongoClient(uri, server_api=ServerApi('1'))

try:
    Mongo_client.admin.command('ping')
    print("✅ Connected to MongoDB Atlas successfully.")
except Exception as e:
    print("❌ MongoDB connection failed:", e)
    exit()

# ✅ Get Gemini API Key
gemini_api_key = os.getenv('GEMINI_API_KEY')
if not gemini_api_key:
    raise ValueError("❌ GEMINI_API_KEY not set in .env file")

# ✅ Set up Gemini client
client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

# ✅ Add a todo
@function_tool
def add_todo(title: str, description: str = "", status: str = "") -> dict:
    try:
        db = Mongo_client["todo_db"]
        collection = db["todos"]
        new_todo = {
            "title": title,
            "description": description,
            "status": status if status else "pending",
            "created_at": datetime.now().isoformat()
        }
        result = collection.insert_one(new_todo)
        return {"id": str(result.inserted_id), **new_todo}
    except Exception as e:
        print(f"Error in add_todo: {e}")
        raise

# ✅ Update a todo
@function_tool
async def update_todo(title: str = None, description: str = None, status: str = None) -> dict:
    try:
        db = Mongo_client["todo_db"]
        collection = db["todos"]
        update_fields = {}
        if title: update_fields["title"] = title
        if description: update_fields["description"] = description
        if status: update_fields["status"] = status

        if not update_fields:
            return {"error": "No fields to update"}

        result = collection.update_one({}, {"$set": update_fields})
        if result.matched_count == 0:
            return {"error": "Todo not found"}
        return {"message": "Todo updated successfully"}
    except Exception as e:
        print(f"Error in update_todo: {e}")
        raise

# ✅ Delete a todo
@function_tool
async def delete_todo(todo_id: str) -> dict:
    try:
        db = Mongo_client["todo_db"]
        collection = db["todos"]
        from bson import ObjectId
        result = collection.delete_one({"_id": ObjectId(todo_id)})
        if result.deleted_count == 0:
            return {"error": "Todo not found"}
        return {"message": "Todo deleted successfully"}
    except Exception as e:
        print(f"Error in delete_todo: {e}")
        raise

# ✅ List todos
@function_tool
async def list_todos(show_completed: bool = False, priority: str = None) -> dict:
    try:
        db = Mongo_client["todo_db"]
        collection = db["todos"]
        query = {}
        if not show_completed:
            query["status"] = {"$ne": "completed"}
        if priority:
            query["priority"] = priority.lower()
        todos = list(collection.find(query))
        for todo in todos:
            todo["_id"] = str(todo["_id"])  # Convert ObjectId to string
        return {"count": len(todos), "todos": todos}
    except Exception as e:
        print(f"Error in list_todos: {e}")
        raise

# ✅ Agent setup
agent = Agent(
    name="Todo Assistant",
    instructions="You are a Todo expert. You can help users with their Todo tasks, lists, and reminders. You can add, delete, update, and fetch user data from MongoDB.",
    model=OpenAIChatCompletionsModel(model="gemini-2.0-flash", openai_client=client),
    tools=[add_todo, list_todos, update_todo, delete_todo]
)

# ✅ Run query
query = input("Enter your query: ")

result = Runner.run_sync(agent, query)

print("\n🔍 Final Output:")
print(result.final_output)




# from pymongo import MongoClient

# Mongo_DB_Connection_String = "mongodb+srv://AgentPractice:AgentPractice@cluster0.yca2x.mongodb.net/?retryWrites=true&w=majority"

# client = MongoClient(Mongo_DB_Connection_String)

# # Test connection
# try:
#     client.admin.command('ping')
#     print("✅ Connected to MongoDB Atlas successfully.")
# except Exception as e:
#     print("❌ Connection failed:", e)
