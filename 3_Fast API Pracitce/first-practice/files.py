from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import shutil
import os
import base64

UPLOAD_FOLDER = "jajja/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = FastAPI()

# Mount the upload folder to serve the uploaded files
app.mount("/static", StaticFiles(directory=UPLOAD_FOLDER), name="static")

@app.get("/")
async def read_root():
    return {"Hello": "server is running, hey danish how are you"}

@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile = File(...)):
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    file_url = f"/static/{file.filename}"
    return {"filename": file.filename, "url": file_url}

@app.get("/filename/{filename}")
async def read_file(filename: str):
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    
    # Check if the file exists
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    # Determine the file type
    if filename.endswith(".txt"):
        # Read text file
        with open(file_path, "r") as file:
            file_content = file.read()
        return JSONResponse(content={"filename": filename, "type": "text", "content": file_content})
    
    elif filename.endswith((".jpg", ".jpeg", ".png", ".gif")):
        # Read image file and encode it as base64
        with open(file_path, "rb") as file:
            file_content = base64.b64encode(file.read()).decode("utf-8")
        return JSONResponse(content={"filename": filename, "type": "image", "content": file_content})
    
    else:
        # Unsupported file type
        return JSONResponse(content={"filename": filename, "type": "unsupported", "message": "File type not supported"})