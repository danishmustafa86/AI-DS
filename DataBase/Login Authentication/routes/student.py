from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from config.database import SessionLocal, engine
from models.student import Student
from pydantic import BaseModel
from typing import List

Student.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = APIRouter()

class StudentCreate(BaseModel):
    ag: int
    name: str
    fullname: str
    password: str
    degree: str

@app.get("/")
def read_root():
    return {"Hello": "Server is runing at todo"}

@app.get("/")
def get_students(db: Session = Depends(get_db)):
    return db.query(Student).all()

@app.get("/{id}")
def get_student(id: int, db: Session = Depends(get_db)):
    return db.query(Student).filter(Student.ag == id).first()

@app.post("/")
def create_student(student: StudentCreate, db: Session = Depends(get_db)):
    try:
        db_student = Student(
            ag=student.ag,
            name=student.name,
            fullname=student.fullname,
            password=student.password,
            degree=student.degree
        )
        db.add(db_student)
        db.commit()
        db.refresh(db_student)
        return db_student
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/{id}")
def update_student(id: int, student: StudentCreate, db: Session = Depends(get_db)):
    try:
        db_student = db.query(Student).filter(Student.ag == id).first()
        db_student.name = student.name
        db_student.fullname = student.fullname
        db_student.password = student.password
        db_student.degree = student.degree
        db.commit()
        db.refresh(db_student)
        return db_student
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/{id}")
def delete_student(id: int, db: Session = Depends(get_db)):
    try:
        db_student = db.query(Student).filter(Student.ag == id).first()
        db.delete(db_student)
        db.commit()
        return {"message": "Student deleted"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))