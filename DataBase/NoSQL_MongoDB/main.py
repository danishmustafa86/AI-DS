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
print("my data base uri is here",MongoDBPractice)


def det_db_client():
    try:
        client = MongoClient(MongoDBPractice)
        print("connected to the database")
        return client
    except Exception as e:
        print("error connecting to database", e)
        return None
    
client = det_db_client()
db = client['todo']



@app.get("/")
def read_root():
    return {"Hello": "server is runing"}

@app.get("/todoos")
def read_todo():
    try:
        todos = db.todo.find()
        listTodos = []
        for val in todos:
            listTodos.append({
                "AG": str(val["AG"]),
                "name": val["name"],
                "Degree": val["degree"],
                "Course": val["Course"]})
        print("there are my listTodos", listTodos,"These are my todos", todos)
        return {
            "data": listTodos,
            "message": "success",
            "status": 200,
            "error":None
        }
    except Exception as e:
        print("error reading todo", e)
        return {
            "data": None,
            "message": "error reading todo",
            "status": 500,
            "error": str(e)
            }