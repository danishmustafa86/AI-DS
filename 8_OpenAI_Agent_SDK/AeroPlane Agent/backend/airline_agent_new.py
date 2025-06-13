from __future__ import annotations as _annotations
import asyncio
import random
import uuid
import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv
from pydantic import BaseModel
from openai import AsyncOpenAI
from agents import (
    Agent,
    HandoffOutputItem,
    ItemHelpers,
    MessageOutputItem,
    RunContextWrapper,
    Runner,
    ToolCallItem,
    ToolCallOutputItem,
    TResponseInputItem,
    function_tool,
    handoff,
    trace,
    OpenAIChatCompletionsModel,
)
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX

load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")
client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

### CONTEXT MODEL

class AirlineAgentContext(BaseModel):
    passenger_name: str | None = None
    confirmation_number: str | None = None
    seat_number: str | None = None
    flight_number: str | None = None
    baggage_tag: str | None = None
    user_id: str | None = None
    email: str | None = None
    preferred_lang: str | None = None

### EMAIL UTIL

def send_email(to_email: str, subject: str, body: str) -> str:
    """Send a plain‐text email and return status."""
    try:
        smtp_server, smtp_port = "smtp.gmail.com", 587
        sender = os.getenv("EMAIL_SENDER")
        password = os.getenv("EMAIL_PASSWORD")
        msg = EmailMessage()
        msg["Subject"], msg["From"], msg["To"] = subject, sender, to_email
        msg.set_content(body)

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender, password)
            server.send_message(msg)

        return f"✅ Email sent to {to_email}"
    except Exception as e:
        return f"❌ Email failed: {e}"

### TOOLS

@function_tool(name_override="faq_lookup_tool", description_override="Lookup frequently asked questions.")
async def faq_lookup_tool(question: str) -> str:
    q = question.lower()
    if "bag" in q or "baggage" in q:
        return "You can bring one bag under 50 lbs and 22×14×9 inches."
    if "seats" in q or "plane" in q:
        return "There are 120 seats: 22 business, 98 economy. Exit rows: 4 & 16. Economy Plus: rows 5-8."
    if "wifi" in q:
        return "Free Wi-Fi onboard: join network 'Airline-Wifi'."
    return "Sorry, I don’t know the answer to that."

@function_tool
async def update_seat(
    context: RunContextWrapper[AirlineAgentContext],
    confirmation_number: str,
    new_seat: str
) -> str:
    context.context.confirmation_number = confirmation_number
    context.context.seat_number = new_seat
    if not context.context.flight_number:
        raise AssertionError("Flight number required")
    return f"Updated seat to {new_seat} for confirmation {confirmation_number}."

@function_tool
async def check_flight_status(flight_number: str) -> str:
    status = random.choice(["On Time", "Delayed", "Cancelled"])
    return f"Flight {flight_number} is currently {status}."

@function_tool
async def track_baggage(tag_number: str) -> str:
    return f"Baggage tag {tag_number} is at Terminal 3, arriving at baggage claim in ~20 mins."

@function_tool
async def reissue_boarding_pass(email: str, confirmation_number: str) -> str:
    body = f"Your boarding pass for booking {confirmation_number}."
    result = send_email(email, "Boarding Pass Re-Issued", body)
    return f"{body} {result}"

@function_tool
async def check_loyalty_points(user_id: str) -> str:
    points = random.randint(1000, 50000)
    return f"User {user_id} has {points} loyalty points."

@function_tool
async def cancel_flight(confirmation_number: str) -> str:
    return f"Flight {confirmation_number} cancelled. Refund will be processed shortly."

@function_tool
async def rebook_flight(confirmation_number: str, new_date: str) -> str:
    return f"Flight {confirmation_number} rebooked to {new_date}."

@function_tool
async def translate_message(message: str, target_language: str) -> str:
    return f"[Translated to {target_language}]: {message}"

@function_tool
async def get_airport_info(airport_code: str) -> str:
    return f"{airport_code} has 3 terminals, VIP lounges in Terminal A, shuttle services every 15 mins."

@function_tool
async def get_invoice(confirmation_number: str, email: str) -> str:
    body = f"Invoice for booking {confirmation_number}."
    result = send_email(email, "Your Flight Invoice", body)
    return f"{body} {result}"

@function_tool
async def request_meal_preference(confirmation_number: str, meal_type: str, email: str) -> str:
    body = f"Meal preference '{meal_type}' confirmed for booking {confirmation_number}."
    result = send_email(email, "Meal Preference Confirmed", body)
    return f"{body} {result}"

@function_tool
async def purchase_travel_insurance(confirmation_number: str, email: str) -> str:
    body = f"Travel insurance activated for booking {confirmation_number}."
    result = send_email(email, "Travel Insurance Confirmation", body)
    return f"{body} {result}"

@function_tool
async def apply_delay_compensation(confirmation_number: str, email: str) -> str:
    body = f"Your delay compensation request for booking {confirmation_number} has been submitted."
    result = send_email(email, "Delay Compensation Submitted", body)
    return f"{body} {result}"

### AGENTS

faq_agent = Agent[AirlineAgentContext](
    name="FAQ Agent",
    handoff_description="Answer standard airline questions.",
    model=OpenAIChatCompletionsModel(model="gemini-2.0-flash", openai_client=client),
    instructions=f"""{RECOMMENDED_PROMPT_PREFIX}
1. Identify the last question.
2. Call faq_lookup_tool.
3. If unknown, transfer back to triage.""",
    tools=[faq_lookup_tool],
)

seat_agent = Agent[AirlineAgentContext](
    name="Seat Booking Agent",
    handoff_description="Update seat assignment.",
    model=OpenAIChatCompletionsModel(model="gemini-2.0-flash", openai_client=client),
    instructions=f"""{RECOMMENDED_PROMPT_PREFIX}
1. Ask for confirmation number.
2. Ask for new seat.
3. Call update_seat tool.""",
    tools=[update_seat],
)

status_agent = Agent[AirlineAgentContext](
    name="Flight Status Agent",
    handoff_description="Check flight status.",
    model=OpenAIChatCompletionsModel(model="gemini-2.0-flash", openai_client=client),
    instructions=f"{RECOMMENDED_PROMPT_PREFIX} Ask flight number, then use check_flight_status tool.",
    tools=[check_flight_status],
)

baggage_agent = Agent[AirlineAgentContext](
    name="Baggage Tracker Agent",
    handoff_description="Track baggage location.",
    model=OpenAIChatCompletionsModel(model="gemini-2.0-flash", openai_client=client),
    instructions=f"{RECOMMENDED_PROMPT_PREFIX} Ask baggage tag, use track_baggage tool.",
    tools=[track_baggage],
)

boarding_pass_agent = Agent[AirlineAgentContext](
    name="Boarding Pass Agent",
    handoff_description="Re-issue boarding pass.",
    model=OpenAIChatCompletionsModel(model="gemini-2.0-flash", openai_client=client),
    instructions=f"{RECOMMENDED_PROMPT_PREFIX} Ask email & confirmation number, use reissue_boarding_pass tool.",
    tools=[reissue_boarding_pass],
)

loyalty_agent = Agent[AirlineAgentContext](
    name="Loyalty Agent",
    handoff_description="Check loyalty points.",
    model=OpenAIChatCompletionsModel(model="gemini-2.0-flash", openai_client=client),
    instructions=f"{RECOMMENDED_PROMPT_PREFIX} Ask user ID, use check_loyalty_points tool.",
    tools=[check_loyalty_points],
)

rebooking_agent = Agent[AirlineAgentContext](
    name="Rebooking Agent",
    handoff_description="Cancel or rebook flights.",
    model=OpenAIChatCompletionsModel(model="gemini-2.0-flash", openai_client=client),
    instructions=f"""{RECOMMENDED_PROMPT_PREFIX}
Ask if user wants to cancel or rebook:
- Cancel: ask confirmation number → cancel_flight
- Rebook: ask confirmation number & new date → rebook_flight
""",
    tools=[cancel_flight, rebook_flight],
)

translator_agent = Agent[AirlineAgentContext](
    name="Translator Agent",
    handoff_description="Translate messages.",
    model=OpenAIChatCompletionsModel(model="gemini-2.0-flash", openai_client=client),
    instructions=f"{RECOMMENDED_PROMPT_PREFIX} Ask target language, then call translate_message.",
    tools=[translate_message],
)

airport_info_agent = Agent[AirlineAgentContext](
    name="Airport Info Agent",
    handoff_description="Airport amenities & directions.",
    model=OpenAIChatCompletionsModel(model="gemini-2.0-flash", openai_client=client),
    instructions=f"{RECOMMENDED_PROMPT_PREFIX} Ask IATA code, then call get_airport_info.",
    tools=[get_airport_info],
)

invoice_agent = Agent[AirlineAgentContext](
    name="Invoice Agent",
    handoff_description="Generate & email invoice.",
    model=OpenAIChatCompletionsModel(model="gemini-2.0-flash", openai_client=client),
    instructions=f"{RECOMMENDED_PROMPT_PREFIX} Ask confirmation number & email, then call get_invoice.",
    tools=[get_invoice],
)

meal_agent = Agent[AirlineAgentContext](
    name="Meal Preference Agent",
    handoff_description="Set meal preference & email user.",
    model=OpenAIChatCompletionsModel(model="gemini-2.0-flash", openai_client=client),
    instructions=f"""{RECOMMENDED_PROMPT_PREFIX}
Ask for confirmation number, meal type, and email.
Call request_meal_preference tool.
""",
    tools=[request_meal_preference],
)

insurance_agent = Agent[AirlineAgentContext](
    name="Insurance Agent",
    handoff_description="Purchase travel insurance & email user.",
    model=OpenAIChatCompletionsModel(model="gemini-2.0-flash", openai_client=client),
    instructions=f"""{RECOMMENDED_PROMPT_PREFIX}
Ask for confirmation number and email.
Call purchase_travel_insurance tool.
""",
    tools=[purchase_travel_insurance],
)

compensation_agent = Agent[AirlineAgentContext](
    name="Compensation Agent",
    handoff_description="Process compensation request & email user.",
    model=OpenAIChatCompletionsModel(model="gemini-2.0-flash", openai_client=client),
    instructions=f"""{RECOMMENDED_PROMPT_PREFIX}
    Ask the user for:
    1. Confirmation number
    2. Email address

    Then call the apply_delay_compensation tool.
    """,

    tools=[apply_delay_compensation],
)

### TRIAGE AGENT

def generate_flight_number(ctx: RunContextWrapper[AirlineAgentContext]) -> None:
    ctx.context.flight_number = f"FLT-{random.randint(100,999)}"

triage_agent = Agent[AirlineAgentContext](
    name="Triage Agent",
    handoff_description="Route requests to the right service agent.",
    instructions=f"""{RECOMMENDED_PROMPT_PREFIX}
    You are a triage agent. Based on the user’s request, transfer them to the correct agent:

    - If the message includes words like "delay", "delayed", "late", "compensation", "refund", or "reimbursement", hand off to the **Compensation Agent**.
    - If the message mentions "seat", "seat change", or "seat number", go to the **Seat Booking Agent**.
    - If it mentions "flight status" or "on time", use **Flight Status Agent**.
    - If it mentions "baggage", "lost bag", or "bag tag", go to **Baggage Tracker Agent**.
    - If it mentions "boarding pass", go to **Boarding Pass Agent**.
    - If it mentions "meal", "food", or "diet", go to **Meal Preference Agent**.
    - If it mentions anything else or is unclear, go to the **FAQ Agent**.
    """,

    handoffs=[
        faq_agent,
        handoff(agent=seat_agent, on_handoff=generate_flight_number),
        status_agent,
        baggage_agent,
        boarding_pass_agent,
        loyalty_agent,
        rebooking_agent,
        translator_agent,
        airport_info_agent,
        invoice_agent,
        meal_agent,
        insurance_agent,
        compensation_agent,
    ],
    model=OpenAIChatCompletionsModel(model="gemini-2.0-flash", openai_client=client),
)

# Close the loop so every agent can hand back to triage
for agent in [
    faq_agent, seat_agent, status_agent, baggage_agent, boarding_pass_agent,
    loyalty_agent, rebooking_agent, translator_agent, airport_info_agent,
    invoice_agent, meal_agent, insurance_agent, compensation_agent
]:
    agent.handoffs.append(triage_agent)

### MAIN LOOP

async def main():
    current_agent = triage_agent
    context = AirlineAgentContext()
    conversation_id = uuid.uuid4().hex[:16]
    input_items: list[TResponseInputItem] = []

    while True:
        user_input = input("Enter your prompt: ")
        with trace("Customer service", group_id=conversation_id):
            input_items.append({"content": user_input, "role": "user"})
            result = await Runner.run(current_agent, input_items, context=context)

            for item in result.new_items:
                if isinstance(item, MessageOutputItem):
                    print(f"{item.agent.name}: {ItemHelpers.text_message_output(item)}")
                elif isinstance(item, HandoffOutputItem):
                    print(f"[:handed off:] {item.source_agent.name} → {item.target_agent.name}")
                elif isinstance(item, ToolCallItem):
                    print(f"{item.agent.name}: 🔧 Calling tool...")
                elif isinstance(item, ToolCallOutputItem):
                    print(f"{item.agent.name}: 🛠 Tool result: {item.output}")

            input_items = result.to_input_list()
            current_agent = result.last_agent

if __name__ == "__main__":
    asyncio.run(main())
