from openai import AsyncOpenAI
from agents import Agent, OpenAIChatCompletionsModel, Runner, function_tool
import os
import requests
from dotenv import load_dotenv
load_dotenv()

gemini_api_key = os.getenv('GEMINI_API_KEY')
client = AsyncOpenAI(
    api_key = gemini_api_key,
    base_url = "https://generativelanguage.googleapis.com/v1beta/openai/",
)

# function to get all user data from github account using github api
@function_tool
def get_github_user_data(username: str) -> str:
    """Fetch user data from GitHub API.
    Args:
        username: The GitHub username to fetch data for.
    
    This function makes a request to the GitHub API to retrieve user data for the specified username.
    If the request is successful, it returns the user data in JSON format.
        Returns:
        A string containing the user data in JSON format or an error message.
        """    
    url = f"https://api.github.com/users/{username}"
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.json()
    else:
        return f"Error fetching data for {username}: {response.status_code} - {response.text}"



agent = Agent(
    name = "Github Assistant",
    instructions = "You are a GitHub expert. You can help users with their GitHub repositories, issues, and pull requests.",
    model = OpenAIChatCompletionsModel(model = "gemini-2.0-flash", openai_client = client),
    tools = [get_github_user_data]
)

query = input("Enter you qyuery: ")

result = Runner.run_sync(
    agent, 
    query,
)

print(result.final_output)