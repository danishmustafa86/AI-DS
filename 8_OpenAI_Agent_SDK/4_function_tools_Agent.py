from openai import AsyncOpenAI
from agents import Agent, OpenAIChatCompletionsModel, Runner, function_tool
import os
from dotenv import load_dotenv
load_dotenv()

gemini_api_key = os.getenv('GEMINI_API_KEY')

client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

@function_tool  
async def fetch_weather(location) -> str:
    """Fetch the weather for a given location.

    Args:
        location: The location to fech the weather for.
    """
    print(f"Fetching weather for {location}...")
    # In real life, we'd fetch the weather from a weather API
    return "sunny"


@function_tool  
def fetch_news(location) -> str:
    """Fetch the news for a given location.

    Args:
        location: The location to fetch the news for.
    """
    print(f"Fetching news for {location}...")
    # In real life, we'd fetch the news from a news API
    return "breaking news"

@function_tool
def fetch_stock_price(location) -> str:
    """Fetch the stock price for a given location.

    Args:
        location: The location to fetch the stock price for.
    """
    print(f"Fetching stok price for {location}...")
    # In real life, we'd fetch the stock price from a stock API
    return "USD 1000.00"

@function_tool
def fetch_my_info(information) -> str:
    """
    Goal: Fetch information about a person.
    Args:
        information: The information to fetch.

    """
    print(f"Fetching my information for {information}...")
    # In real life, we'd fetch the information from a database or an API
    return f"My {information} is confidential and not available for public access. Please contact support for more information."


agent = Agent(
    name="Assistant",
    instructions="You are an expert of agentic AI.",
    model=OpenAIChatCompletionsModel(model="gemini-2.0-flash", openai_client=client),
    tools=[fetch_weather, fetch_news, fetch_stock_price, fetch_my_info],
)

query = input("Enter the query: ")

result = Runner.run_sync(
    agent,
    query,
)

print(result.final_output)