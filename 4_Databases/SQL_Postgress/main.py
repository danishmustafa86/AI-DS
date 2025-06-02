from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from config.database import SessionLocal, engine
from models.todo_model import Todo
from pydantic import BaseModel
from typing import Optional
import time

Todo.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency for DB session is below
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic model for validation
class TodoCreate(BaseModel):
    title: str
    name: Optional[str] = None  # Fix: Use Optional[str]
    description: Optional[str] = None  # Fix: Use Optional[str]
    completed: bool = False
    timestamp: int = int(time.time())

class TodoResponse(TodoCreate):
    id: int
    class Config:
        from_attributes = True

@app.get("/")
def read_root():
    return {"message": "Welcome to Todo API"}

# Create a new Todo
@app.post("/todos/", response_model=TodoResponse)
def create_todo(todo: TodoCreate, db: Session = Depends(get_db)):
    db_todo = Todo(
        title=todo.title, 
        description=todo.description, 
        completed=todo.completed, 
        timestamp=todo.timestamp, 
        name=todo.name
    )
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo

# Get all Todos
@app.get("/todoos/")
def get_todos(db: Session = Depends(get_db)):
    return db.query(Todo).all()

# Get a Todo by ID
@app.get("/todoos/{todo_id}", response_model=TodoResponse)
def get_todo(todo_id: int, db: Session = Depends(get_db)):
    todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo

# Update a Todo
@app.put("/todoos/{todo_id}", response_model=TodoResponse)
def update_todo(todo_id: int, todo_update: TodoCreate, db: Session = Depends(get_db)):
    todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")

    todo.title = todo_update.title
    todo.description = todo_update.description
    todo.completed = todo_update.completed
    todo.timestamp = int(time.time())  # Fix: Update timestamp on modification

    db.commit()
    db.refresh(todo)
    return todo

# Delete a Todo
@app.delete("/todoos/{todo_id}", response_model=dict)
def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    db.delete(todo)
    db.commit()
    return {"message": "Todo deleted"}

# Delete a Todo
@app.delete("/todoos/{todo_id}", response_model=dict)
def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    db.delete(todo)
    db.commit()
    return {"message": "Todo deleted successfully"}