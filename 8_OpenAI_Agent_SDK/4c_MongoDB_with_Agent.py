from openai import AsyncOpenAI
from agents import Agent, OpenAIChatCompletionsModel, Runner, function_tool
import os
from datetime import datetime, timedelta 
import requests
from dotenv import load_dotenv
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
load_dotenv()
uri = os.getenv('Mongo_DB_Connection_String')
Mongo_client = MongoClient(uri, server_api=ServerApi('1'))
# Send a ping to confirm a successful connection
try:
    Mongo_client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)


gemini_api_key = os.getenv('GEMINI_API_KEY')
client = AsyncOpenAI(
    api_key = gemini_api_key,
    base_url = "https://generativelanguage.googleapis.com/v1beta/openai/",
)



# Add a todo to the MongoDB database
@function_tool
def add_todo(title: str, description: str = "", status:str = "") -> dict:
    """Add a new todo to the MongoDB database."""
    try:
        db = Mongo_client["todo_db"]
        collection = db["todos"]
        
        new_todo = {
            "title": title,
            "description": description,
            "status": "pending",  # Default status
            "created_at": datetime.now().isoformat()
        }
        
        result = collection.insert_one(new_todo)
        return {"id": str(result.inserted_id), **new_todo}
    except Exception as e:
        print(f"Error: {e}")
        raise


# Update a todo in the MongoDB database
@function_tool
async def update_todo( title: str = None, description: str = None, status: str = None) -> dict:
    """Update an existing todo in the MongoDB database."""
    try:
        db = Mongo_client["todo_db"]
        collection = db["todos"]
        
        update_fields = {}
        if title is not None:
            update_fields["title"] = title
        if description is not None:
            update_fields["description"] = description
        if status is not None:
            update_fields["status"] = status
        
        if not update_fields:
            return {"error": "No fields to update"}
        
        result = collection.update_one( {"$set": update_fields})
        
        if result.matched_count == 0:
            return {"error": "Todo not found"}
        
        return {"message": "Todo updated successfully"}
    except Exception as e:
        print(f"Error: {e}")
        raise

# Delete a todo from the MongoDB database
@function_tool
async def delete_todo(todo_id: str) -> dict:
    """Delete a todo from the MongoDB database."""
    try:
        db = Mongo_client["todo_db"]
        collection = db["todos"]
        
        result = collection.delete_one({"_id": todo_id})
        
        if result.deleted_count == 0:
            return {"error": "Todo not found"}
        
        return {"message": "Todo deleted successfully"}
    except Exception as e:
        print(f"Error: {e}")
        raise

# Function to list all todos from the MongoDB database
@function_tool
async def list_todos(show_completed: bool = False, priority: str = None) -> dict:
    """List all todos from the MongoDB database."""
    try:
        db = Mongo_client["todo_db"]
        collection = db["todos"]
        
        query = {}
        if not show_completed:
            query["completed"] = False
        if priority:
            query["priority"] = priority.lower()
        
        todos = list(collection.find(query))
        for todo in todos:
            todo["_id"] = str(todo["_id"])  # Convert ObjectId to string for JSON serialization
        
        return {"count": len(todos), "todos": todos}
    except Exception as e:
        print(f"Error: {e}")
        raise





agent = Agent(
    name = "Todo Assistant",
    instructions = "You are a Todo expert. You can help users with their Todo tasks, lists, and reminders.You can add user data in his database, delete, update and fetch user data.",  
    model = OpenAIChatCompletionsModel(model = "gemini-2.0-flash", openai_client = client),
    tools = [add_todo, list_todos, update_todo, delete_todo]
)

query = input("Enter you query: ")

result = Runner.run_sync(
    agent, 
    query,
)

print(result.final_output)