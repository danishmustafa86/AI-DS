from fastapi import FastAPI
from pymongo import MongoClient
from datetime import datetime
from bson.objectid import ObjectId
from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()
app = FastAPI()
MongoDBPractice = os.getenv("MongoDBPractice")
print("My database URI is here:", MongoDBPractice)

def det_db_client():
    try:
        client = MongoClient(
            MongoDBPractice,
            tls=True,  # Enable SSL/TLS
            tlsAllowInvalidCertificates=True,  # Allow invalid certificates (for debugging)
            serverSelectionTimeoutMS=5000  # Set a timeout for server selection
        )
        client.server_info()  # Test the connection
        print("Connected to the database")
        return client
    except Exception as e:
        print("Error connecting to the database:", e)
        return None

client = det_db_client()
if client is None:
    print("Failed to connect to te database. Exiting...")
    exit(1)  # Exit the program with an error code
db = client['MongoLearning']

@app.get("/")
def read_root():
    return {"Hello": "Server is running"}

@app.get("/todoos")
def read_todo():
    try:
        todos = db.todo.find()
        listTodos = []
        for val in todos:
            listTodos.append({
                "AG": str(val["AG"]),
                "name": val["name"],
                "Degree": val["Degree"],
                "Course": val["Course"]
            })
        print("Here are my listTodos:", listTodos)
        return {
            "data": listTodos,
            "message": "Success",
            "status": 200,
            "error": None
        }
    except Exception as e:
        print("Error reading todo:", e)
        return {
            "data": None,
            "message": "Error reading todo",
            "status": 500,
            "error": str(e)
        }

@app.get("/todoos/{AG}")
def read_todo_by_AG(AG: str):
    try:
        AG_todo = db.todo.find_one({"AG":AG})
        if AG_todo is None:
            return {
                "data": None,
                "message": "Todo not found",
                "status": 404,
                "error": None
            }
        return {
            "data": {
                "AG": str(AG_todo["AG"]),
                "name": AG_todo["name"],
                "Degree": AG_todo["Degree"],
                "Course": AG_todo["Course"]
            },
            "message": "Success",
            "status": 200,
            "error": None
        }
    except Exception as e:
        print("Error reading todo:", e)
        return {
            "data": None,
            "message": "Error reading todo",
            "status": 500,
            "error": str(e)
        }


class Todo(BaseModel):  
    name: str
    Degree: str
    Course: str
    AG: str

@app.post("/todoos")
def create_todo(todo: Todo):
    try:
        db.todo.insert_one({
            "AG": todo.AG,
            "name": todo.name,
            "Degree": todo.Degree,
            "Course": todo.Course
        })
        return {
            "data": {
                "AG": todo.AG,
                "name": todo.name,
                "Degree": todo.Degree,
                "Course": todo.Course
            },
            "message": "Todo created successfully",
            "status": 201,
            "error": None
        }
    except Exception as e:
        print("Error creating todo:", e)
        return {
            "data": None,
            "message": "Error creating todo",
            "status": 500,
            "error": str(e)
        }

@app.put("/todoos/{AG}")
def update_todo_by_AG(AG: str, todo: Todo):
    try:
        db.todo.update_one({"AG": AG}, {"$set": {
            "name": todo.name,
            "Degree": todo.Degree,
            "Course": todo.Course,
            "AG": todo.AG
        }})
        return {
            "data": {
                "AG": AG,
                "name": todo.name,
                "Degree": todo.Degree,
                "Course": todo.Course
            },
            "message": "Todo updated successfully",
            "status": 200,
            "error": None
        }
    except Exception as e:
        print("Error updating todo:", e)
        return {
            "data": None,
            "message": "Error updating todo",
            "status": 500,
            "error": str(e)
        }
    
@app.delete("/todoos/{AG}")
def delete_todo_by_AG(AG: str):
    try:
        db.todo.delete_one({"AG": AG})
        print("Todo deleted successfully")
        return {
            "data": None,
            "message": "Todo deleted successfully",
            "status": 200,
            "error": None   
        }
    except Exception as e:
        print("Error in deleting todo:", e)
        return {
            "data": None,
            "message": "Error deleting todo",
            "status": 500,
            "error": str(e)
        }