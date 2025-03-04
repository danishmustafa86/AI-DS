
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from config.database import SessionLocal, engine
from models.todo import Todo
from pydantic import BaseModel
from typing import List

Todo.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = APIRouter()

class TodoCreate(BaseModel):
    title: str
    description: str
    status: str
    user_id: int

@app.get("/")
def read_root():
    return {"Hello": "Server is runing at todo"}

@app.get("/{id}")
def get_todos(id: int, db: Session = Depends(get_db)):
    return db.query(Todo).filter(Todo.user_id == id).all()

@app.post("/")
def create_todos(todo: TodoCreate, db: Session = Depends(get_db)):
    try:
        db_todo = Todo(
            title=todo.title,
            description=todo.description,
            status=todo.status,
            user_id=todo.user_id
        )
        db.add(db_todo)
        db.commit()
        db.refresh(db_todo)
        return db_todo
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/{id}")
def update_todos(id: int, todo: TodoCreate, db: Session = Depends(get_db)):
    try:
        db_todo = db.query(Todo).filter(Todo.user_id == id).first()
        db_todo.title = todo.title
        db_todo.description = todo.description
        db_todo.status = todo.status
        db.commit()
        db.refresh(db_todo)
        return db_todo
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/{id}")
def delete_todos(id: int, db: Session = Depends(get_db)):
    try:
        db_todo = db.query(Todo).filter(Todo.user_id == id).first()
        db.delete(db_todo)
        db.commit()
        return {"message": "Todo deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))