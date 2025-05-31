from pydantic import BaseModel
import os
import asyncio
from openai import AsyncOpenAI
from dotenv import load_dotenv
from agents import (
    Agent,
    GuardrailFunctionOutput,
    InputGuardrailTripwireTriggered,
    RunContextWrapper,
    Runner,
    TResponseInputItem,
    input_guardrail,
    OpenAIChatCompletionsModel
)

gemini_api_key = os.getenv('GEMINI_API_KEY')
load_dotenv()

class MathHomeworkOutput(BaseModel):
    is_math_homework: bool
    reasoning: str

client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)


guardrail_agent = Agent( 
    name="Guardrail check",
    instructions="Check if the user is asking you to do their math homework.",
    model = OpenAIChatCompletionsModel(model="gemini-2.0-flash", openai_client=client),
    output_type=MathHomeworkOutput,
)

query = "How can i assist you today? "

@input_guardrail
async def math_guardrail( 
    ctx: RunContextWrapper[None], agent: Agent, input: str | list[TResponseInputItem]
) -> GuardrailFunctionOutput:
    result = await Runner.run(guardrail_agent, input, context=ctx.context)

    return GuardrailFunctionOutput(
        output_info=result.final_output, 
        tripwire_triggered=result.final_output.is_math_homework,
    )


main_agent = Agent(  
    name="Customer support agent",
    instructions="You are a customer support agent. You help customers with their questions.",
    input_guardrails=[math_guardrail],
    model=OpenAIChatCompletionsModel(model="gemini-2.0-flash", openai_client=client),
)


async def main():
    query = input("Enter your query: ")
    # This should trip the guardrail
    try:
        result = await Runner.run(main_agent, query)
        print(f"Guardrail didn't trip - this is unexpected { result.final_output}")

    except InputGuardrailTripwireTriggered:
        print("Math homework guardrail tripped")


if __name__ == "__main__":
    asyncio.run(main())