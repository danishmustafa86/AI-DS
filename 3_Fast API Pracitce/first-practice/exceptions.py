from fastapi import HTTPException, FastAPI, UploadFile, File, requests
from pydantic import BaseModel, EmailStr, Field
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

app = FastAPI()

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: requests, exc: RequestValidationError):
    errors = []
    for error in exc.errors():
        errors.append({"field": ".".join(map(str,error["loc"])), "message": error["msg"]})
    return JSONResponse(
        status_code=400,
        content= {
            "status": "error",
            "errors": errors,
            "message": "validation error"
        }
    )

@app.get("/")
async def read_root():
    return {"Hello": "server is running"}

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    return {"filename": file.filename}

# pydantic validations
class User(BaseModel):
    username: str
    email: EmailStr
    password: str = Field(..., min_length=8)
@app.get("/items/{item_id}")
async def read_item(item_id: int, q: str = None, user: User = None):
    if user is None:
        raise HTTPException(status_code=400, detail="invalid user")
    return {"item_id": item_id}