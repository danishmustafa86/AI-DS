from fastapi import FastAPI

# print("hello jajja")
app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello, World! how are you"}

@app.post("/items/")
def create_item(item: dict):
    return {"item": item}