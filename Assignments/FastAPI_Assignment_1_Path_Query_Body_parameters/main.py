from fastapi import FastAPI, HTTPException, Query, Path
from pydantic import  EmailStr, BaseModel, Field, validator
from typing import Optional, List

app = FastAPI()


class EmailUpdate(BaseModel):
    email: EmailStr

class Student(BaseModel):
    name:str = Field(..., min_length=3, max_length=50,pattern="^[a-zA-Z]+$",description="Name must contain 3 to 50 characters")
    email:EmailStr = Field(...,description="Email must be valid")
    age:int  = Field(..., gt = 18, lt = 30, description = "Age must be between 18 to 30")
    courses:List[str] = Field(..., min_items = 1, max_items = 5, description=("Courses must be between 1 to 5"))

    @validator("courses")
    def check_courses(cls, courses):
        for course in courses:
            if len(course) < 3 or len(course) > 30:
                raise ValueError("Course name must be between 5 to 30 characters")
        return courses
Student_Data = {
    1001: {
        "name": "Danish",
        "email": "danish@gmail.com", 
        "age": 20,
        "courses": ["Math", "Science", "History"]
    },
    1002: {
        "name": "Mustafa",
        "email": "mustafa@gmail.com",
        "age": 22,
        "courses": ["Math", "Science", "Geography"]
    },
    1003: {
        "name": "Ahmad",
        "email": "ahmad@gmail.com",
        "age": 25,
        "courses": ["Math", "Science", "English"]
    },
    1004: {
        "name": "Ali",
        "email": "ali@gmail.com",
        "age": 18,
        "courses": ["Math", "Science", "History"]
    },
}

@app.get("/")
def read_root():
    return {"Student Management System": "Welcome to Student Management System"}

@app.get("/students/{student_id}")
def studentform(    
    student_id: int = Path(..., gt=1000, lt=9999, description="Student ID must be between 1000 to 9999"),
    include_grades: bool = Query(True, description="Include grades in response"),
    semester: Optional[str] = Query(None, regex="^(Fall|Spring|Summer)\d{4}$", description="Semester must be in the format Fall2024, Spring2025, etc.")
):

    try:
        if student_id not in Student_Data:
            raise HTTPException(status_code=404, detail="Student not found")

        return {
            "student_id": student_id,
            "include_grades": include_grades,
            "semester": semester
        }
    except Exception as e:
        return {
            "message": str(e),
            "error": "Invalid input",
            "status": 400
                }
    
@app.post("/students/register")
def register_student(student: Student):
    try:
        if student.age < 18 or student.age > 30:
            raise HTTPException(status_code=400, detail="Age must be between 18 to 30")
        return {
            "student": student

        }
    except Exception as e:
        return {
            "message": str(e),
            "error": "Invalid input",
            "status": 400
                }
    
@app.put("/students/{student_id}/email")
def update_student_email(student_id: int,email_update: EmailUpdate):
    try:
        if student_id not in Student_Data:
            raise HTTPException(status_code=404, detail="Student not found")
        if student_id <= 1000 or student_id >= 9999:
            raise ValueError("Invalid student id")
        Student_Data[student_id]["email"] = email_update.email
        return {
            "student": student_id,
            "email": email_update.email

        }
    except Exception as e:
        return {
            "message": str(e),
            "error": "Invalid input",
            "status": 400
                }
    