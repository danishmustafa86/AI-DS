from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Student(Base):
    __tablename__ = "students"
    ag = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    fullname = Column(String, index=True)
    password = Column(String)
    degree = Column(String)
    email = Column(String, index=True)