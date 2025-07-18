from openai import AsyncOpenAI #type ignore
from agents import Agent, OpenAIChatCompletionsModel, Runner # type: ignore
import os
from dotenv import load_dotenv 


load_dotenv()

gemini_api_key = os.getenv('GEMINI_API_KEY')

client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)



agent = Agent(
    name="Assistant",
    instructions="You are an expert of agentic AI with additional features like Tech expert in every feild of AI.",
    model=OpenAIChatCompletionsModel(model="gemini-2.0-flash", openai_client=client),
)

query = input("Enter the query: ")

result = Runner.run_sync(
    agent,
    query,
)

print(result.final_output)