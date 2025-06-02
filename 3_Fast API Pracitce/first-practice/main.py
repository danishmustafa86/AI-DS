from fastapi import FastAPI

# print("hello jajja")
app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello, World! how are you, are you fine, sorry i am not fine"}


@app.get("/login")
def read_root():
    print("hello jajja")
    return {"message": "Hello, World! how are you, are you fine login, sorry i am not fine"}

@app.post("/login")
def read_root():
    print("hello jajja")
    return {"message": "Hello, World! how are you, are you fine login post, sorry i am not fine"}

@app.delete("/login")
def read_root():
    print("hello jajja")
    return {"message": "Hello, World! how are you, are you fine login delete, sorry i am not fine"}

@app.delete("/auth")
def deleteFunction():
    return {"message": "Hello, World! how are you, are you fine delete function, sorry i am not fine, I want to delete something."}

@app.post("/items/signup")
def create_item():
    return {"item": "I am danish mustafa items signup, a student at university of agricuture fisalabad"}

@app.put("/items")
def create_item():
    return {"item": "I am danish mustafa, a student at university of agricuture fisalabad"}