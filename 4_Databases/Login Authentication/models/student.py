from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Student(Base):
    __tablename__ = "students"
    email = Column(String, primary_key=True, index=True)
    ag = Column(Integer, index=True)
    name = Column(String, index=True)
    fullname = Column(String, index=True)
    password = Column(String)
    degree = Column(String)