# poetry run alembic revision --autogenerate -m "create todos table"
# poetry run alembic upgrade head

from fastapi import FastAPI
from dotenv import load_dotenv
from routes import student, todo

load_dotenv()

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "Server is runing at main page"}
app.include_router(student.app, prefix="/students", tags=["students"])
app.include_router(todo.app, prefix="/todos", tags=["todos"])

