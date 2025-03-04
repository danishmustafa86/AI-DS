from fastapi import FastAPI
from dotenv import load_dotenv
from routes import student, todo

load_dotenv()

app = FastAPI()

app.include_router(student.app, prefix="/students", tags=["students"])
app.include_router(todo.app, prefix="/todos", tags=["todos"])
#         raise HTTPException(status_code=400, detail=str(e))
