from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio

app = FastAPI()

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this in production to your frontend's domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request body model
class PromptInput(BaseModel):
    prompt: str


# Shared state
chat_context = None
conversation_id = None
current_agent = None
input_items = []

@app.on_event("startup")
async def startup():
    global current_agent, chat_context, conversation_id, input_items
    from airline_agent import triage_agent, AirlineAgentContext
    import uuid

    chat_context = AirlineAgentContext()
    conversation_id = uuid.uuid4().hex[:16]
    input_items = []
    current_agent = triage_agent

@app.post("/chat")
async def chat(input_data: PromptInput):
    from airline_agent import (
        Runner,
        MessageOutputItem,
        HandoffOutputItem,
        ToolCallItem,
        ToolCallOutputItem,
        ItemHelpers,
        trace,
    )

    global current_agent, chat_context, input_items

    input_items.append({"content": input_data.prompt, "role": "user"})

    output_text = ""

    with trace("Customer service"):
        result = await Runner.run(current_agent, input_items, context=chat_context)

        for item in result.new_items:
            if isinstance(item, MessageOutputItem):
                output_text += ItemHelpers.text_message_output(item)
            elif isinstance(item, ToolCallOutputItem):
                output_text += f"\n🛠 Tool result: {item.output}"
            elif isinstance(item, HandoffOutputItem):
                # 🔁 handle agent switch
                print(f"🔁 Switching from {item.source_agent.name} to {item.target_agent.name}")
                current_agent = item.target_agent
                output_text += f"\n➡️ Transferring you to {item.target_agent.name}."

        input_items = result.to_input_list()
        current_agent = result.last_agent

    return {"response": output_text}
