from fastapi import FastAPI, HTTPException, Depends, Query, Path
from pydantic import EmailStr, BaseModel, Field, validator
from typing import Optional, List
from bson import ObjectId
from database import student_collection, student_helper


app = FastAPI()

class StudentCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=50, pattern="^[a-zA-Z]+$", description="Name must contain 3 to 50 characters")
    email: EmailStr = Field(..., description="Email must be valid")
    age: int = Field(..., gt=18, lt=30, description="Age must be between 18 to 30")
    courses: List[str] = Field(..., min_items=1, max_items=5, description="Courses must be between 1 to 5")

    @validator("courses")
    def check_courses(cls, courses):
        for course in courses:
            if len(course) < 5 or len(course) > 30:
                raise ValueError("Course name must be between 5 to 30 characters")
        return courses

class EmailUpdate(BaseModel):
    email: EmailStr

@app.get("/")
def read_root():
    return {"Student Management System": "Welcome to Student Management System"}

@app.get("/students/{student_id}")
async def get_student(student_id: str):
    student = await student_collection.find_one({"_id": ObjectId(student_id)})
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    return student_helper(student)

@app.post("/students/register")
async def register_student(student: StudentCreate):
    student = student.dict()
    new_student = await student_collection.insert_one(student)
    created_student = await student_collection.find_one({"_id": new_student.inserted_id})
    return student_helper(created_student)

@app.put("/students/{student_id}/email")
async def update_student_email(student_id: str, email_update: EmailUpdate):
    updated_student = await student_collection.update_one(
        {"_id": ObjectId(student_id)}, {"$set": {"email": email_update.email}}
    )
    if updated_student.modified_count == 0:
        raise HTTPException(status_code=404, detail="Student not found")
    student = await student_collection.find_one({"_id": ObjectId(student_id)})
    return student_helper(student)

@app.delete("/students/{student_id}")
async def delete_student(student_id: str):
    delete_result = await student_collection.delete_one({"_id": ObjectId(student_id)})
    if delete_result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Student not found")
    return {"detail": "Student deleted"}
