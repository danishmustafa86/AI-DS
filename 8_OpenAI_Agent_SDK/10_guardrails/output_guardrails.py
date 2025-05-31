from pydantic import BaseModel
import os
import asyncio
from openai import AsyncOpenAI
from dotenv import load_dotenv
from agents import (
    Agent,
    GuardrailFunctionOutput,
    OutputGuardrailTripwireTriggered,
    RunContextWrapper,
    Runner,
    output_guardrail,
    OpenAIChatCompletionsModel
)

load_dotenv()
gemini_api_key = os.getenv('GEMINI_API_KEY')


client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)
class MessageOutput(BaseModel): 
    response: str

class MathOutput(BaseModel): 
    reasoning: str
    is_math: bool

guardrail_agent = Agent(
    name="Guardrail check",
    instructions="Check if the output includes any math.",
    model=OpenAIChatCompletionsModel(model="gemini-2.0-flash", openai_client=client),
    output_type=MathOutput,
)

@output_guardrail
async def math_guardrail(  
    ctx: RunContextWrapper, agent: Agent, output: MessageOutput
) -> GuardrailFunctionOutput:
    result = await Runner.run(guardrail_agent, output.response, context=ctx.context)

    return GuardrailFunctionOutput(
        output_info=result.final_output,
        tripwire_triggered=result.final_output.is_math,
    )

agent = Agent( 
    name="Customer support agent",
    instructions="You are a customer support agent. You help customers with their questions.",
    model=OpenAIChatCompletionsModel(model="gemini-2.0-flash", openai_client=client),
    output_guardrails=[math_guardrail],
    output_type=MessageOutput,
)

async def main():
    query = input("Enter your query: ")
    # This should trip the guardrail
    try:
        result = await Runner.run(agent, query)
        print("Guardrail didn't trip - this is unexpected", result.final_output)

    except OutputGuardrailTripwireTriggered:
        print("Math output guardrail tripped")

if __name__ == "__main__":
    asyncio.run(main())