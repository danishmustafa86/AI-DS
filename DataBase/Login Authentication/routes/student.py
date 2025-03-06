from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from config.database import SessionLocal, engine
from models.student import Student
from pydantic import BaseModel
from typing import List
from utils.utils_helper import create_access_token, decode_access_token
from validations.validations import StudentCreate, LoginStudent

Student.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app = APIRouter()



@app.get("/")
def read_root():
    return {"Hello": "Server is runing at todo"}


@app.post("/register")
def register_student(student: StudentCreate, db: Session = Depends(get_db)):
    try:
        db_student = Student(
            ag=student.ag,
            name=student.name,
            fullname=student.fullname,
            password=student.password,
            degree=student.degree,
            email=student.email
        )
        db.add(db_student)
        db.commit()
        db.refresh(db_student)
        return {
            "message": "Student created successfully",
            "data": db_student,
            "status": 200

        }
    except Exception as e:
        return {
            "message": "An error occurred",
            "status": 400,
            "error": str(e)
        }

@app.post("/login")
def login_student(student: LoginStudent, db: Session = Depends(get_db)):
    try:
        db_student = db.query(Student).filter(Student.email == student.email).first()
        if db_student is None:
            return {
                "message": "Invalid credentials",
                "status": 401
            }
        if db_student.password != student.password:
            return {
                "message": "Invalid password",
                "status": 401
            }
        access_token = create_access_token(data={"sub": db_student.email})
        return {
            "access_token": access_token,
            "token_type": "bearer"
        }
    except Exception as e:
        return {
            "message": "An error occurred",
            "status": 400,
            "error": str(e)
        }
        
        
        

     







@app.get("/{id}")
def get_student(id: int, db: Session = Depends(get_db)):
    return db.query(Student).filter(Student.ag == id).first()


@app.put("/{id}")
def update_student(id: int, student: StudentCreate, db: Session = Depends(get_db)):
    try:
        db_student = db.query(Student).filter(Student.ag == id).first()
        db_student.name = student.name
        db_student.fullname = student.fullname
        db_student.password = student.password
        db_student.degree = student.degree
        db_student.email = student.email
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