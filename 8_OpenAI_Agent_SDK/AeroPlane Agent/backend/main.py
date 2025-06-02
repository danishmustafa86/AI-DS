from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models import MessageInput, MessageResponse
from database import store_user_message
from agents_module import process_user_input

app = FastAPI()

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

import traceback

@app.post("/api/message", response_model=MessageResponse)
async def chat_with_agent(msg: MessageInput):
    try:
        result = await process_user_input(msg.user_id, msg.message)
        store_user_message(msg.user_id, msg.message, result)
        return MessageResponse(response=result)
    except Exception as e:
        print("🔥 Server Error:", e)
        traceback.print_exc()  # <-- This shows the full stack trace in terminal
        raise HTTPException(status_code=500, detail=str(e))

