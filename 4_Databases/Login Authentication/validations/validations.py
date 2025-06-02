from pydantic import BaseModel, Field, AfterValidator
from typing import List
from typing_extensions import Annotated



class TodoCreate(BaseModel):
    title: str
    description: str
    status: str
    user_id: int

class StudentCreate(BaseModel):
    ag: int
    name: str
    fullname: str
    password: str
    degree: str
    email: str

class LoginStudent(BaseModel):
    email: str
    password: str