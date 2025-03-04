# uv run alembic revision --autogenerate -m "create todos table"
# uv run alembic upgrade head

from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from config.database import SessionLocal, engine
from models.student import User
from pydantic import BaseModel
from typing import List


User.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class UserCreate(BaseModel):
    name: str
    fullname: str
    password: str
    title: str
    id: int

@app.get("/")
def read_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users

@app.get("/{user_id}")
def get_user_by_id(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.post("/")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = User(id=user.id, name=user.name, fullname=user.fullname, password=user.password, title=user.title)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.put("/{user_id}")
def update_user(user_id: int, user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    db_user.name = user.name
    db_user.fullname = user.fullname
    db_user.password = user.password
    db_user.title = user.title
    db.commit()
    db.refresh(db_user)
    return db_user

@app.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(db_user)
    db.commit()
    return {"message": "User deleted successfully"}