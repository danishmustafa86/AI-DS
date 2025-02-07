from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import time
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_process_time_header(request, call_next):
    print("requests", request)
    print("call_next", call_next)
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    print("start time is", start_time, "process time is", process_time)
    print("response testing", response)
    return response

@app.get("/")
async def read_root():
    return {"Hello": "server is running by testing middleware"}

@app.post("/posts/")
async def create_post():
    time.sleep(2)
    return {"status": "post created",
            "data":{"posts":[{"title": "post 1", "content": "content 1"},
                             {"title": "post 2", "content": "content 2"},
                             {"title": "post 3", "content": "content 3"},
                             {"title": "post 4", "content": "content 4"}]}}
            

@app.get("/abc")
async def abc_route():
    return {"message": "this is abc route"}
