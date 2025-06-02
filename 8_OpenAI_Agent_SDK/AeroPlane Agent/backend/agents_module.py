import uuid
from agents import Runner, TResponseInputItem
from airline_agent import triage_agent, AirlineAgentContext

# Store per-session context
context_map = {}

async def process_user_input(user_id: str, message: str) -> str:
    if user_id not in context_map:
        context_map[user_id] = AirlineAgentContext()

    input_items: list[TResponseInputItem] = [{"content": message, "role": "user"}]
    context = context_map[user_id]

    result = await Runner.run(triage_agent, input_items, context=context)
    responses = []

    for new_item in result.new_items:
        if hasattr(new_item, "output"):
            responses.append(str(new_item.output))
        elif hasattr(new_item, "message"):
            responses.append(new_item.message.content)

    return "\n".join(responses)
