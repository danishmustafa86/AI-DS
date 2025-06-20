from pprint import pprint
from typing import Annotated
from typing_extensions import TypedDict #type: ignore
from langchain_core.messages import AnyMessage #type: ignore
from langgraph.graph.message import add_messages #type: ignore
from langchain_core.messages import AIMessage, HumanMessage #type: ignore
from langgraph.prebuilt import ToolNode #type: ignore
from langgraph.prebuilt import tools_condition #type: ignore
from langgraph.graph import StateGraph, START, END #type: ignore
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAI #type: ignore
from dotenv import load_dotenv #type: ignore
import os
load_dotenv()

llm = ChatGoogleGenerativeAI( model="gemini-1.5-flash", google_api_key=os.getenv("GEMINI_API_KEY"))


messages = [AIMessage(content=f"So you said you were researching ocean mammals?", name="Model")]

messages.append(HumanMessage(content=f"Yes, that's right.",name="Lance"))
messages.append(AIMessage(content=f"Great, what would you like to learn about.", name="Model"))
messages.append(HumanMessage(content=f"I want to learn about the best place to see Orcas in the US.", name="Lance"))


def add(a: int, b: int) -> int:
    """Add a and b.

    Args:
        a: first int
        b: second int
    """
    return a + b

def subtract(a: int, b: int) -> int:
    """Subtract b from a.
    Args:
        a: first int
        b: second int
    """
    return a - b

def square(a: int) -> int:
    """Square a.
    Args:
        a: int to square
    """
    return a * a

def divide(a: int, b: int) -> float:
    """Dividee  a by b.

    Args:
        a: first integ
        b: second int
    """
    if b == 0:
        raise ValueError("Cannot divide by zero.")
    return a / b

def multiply(a: int, b: int) -> int:
    """Multiply a and b.

    Args:
        a: first int
        b: second int
    """
    return a * b

llm_with_tools = llm.bind_tools([multiply, subtract, square, add, divide])



class MessagesState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    


def tool_calling_llm(state: MessagesState):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}

# Build graph
builder = StateGraph(MessagesState)
builder.add_node("tool_calling_llm", tool_calling_llm)
builder.add_node("tools", ToolNode([multiply, subtract, square, add, divide]))
builder.add_edge(START, "tool_calling_llm")
builder.add_conditional_edges(
    "tool_calling_llm",
    tools_condition,
)
builder.add_edge("tools", END)
graph = builder.compile()

messages = graph.invoke({"messages": HumanMessage(content="what is result of subtracting of 10 by 2?")})
for m in messages['messages']:
    m.pretty_print()
