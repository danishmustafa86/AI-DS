from pydantic import BaseModel

class MessageInput(BaseModel):
    user_id: str
    message: str

class MessageResponse(BaseModel):
    response: str
