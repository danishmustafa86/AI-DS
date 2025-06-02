# filepath: /D:/Programming/AI-DS With Naveed/DataBase/SQL_Postgress/models/todo_model.py
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Todo(Base):
    __tablename__ = 'todos'
    id = Column(Integer, primary_key=True)
    title = Column(String(255))
    done = Column(Boolean, default=False)
    name = Column(Boolean, default=False)
    completed = Column(Boolean, default=False)