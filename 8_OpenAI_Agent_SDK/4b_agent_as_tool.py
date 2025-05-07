import json
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List
import asyncio

import streamlit as st
from dotenv import load_dotenv
from openai import AsyncOpenAI
from agents import Agent, OpenAIChatCompletionsModel, Runner, function_tool

# Load environment variables
load_dotenv()
gemini_api_key = os.getenv('GEMINI_API_KEY')

# Initialize OpenAI client with Gemini base URL
client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

# --- Todo Functions ---
def load_todos() -> List[Dict]:
    try:
        with open("todos.json", "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_todos(todos: List[Dict]):
    with open("todos.json.tmp", "w") as file:
        json.dump(todos, file, indent=2)
    os.replace("todos.json.tmp", "todos.json")

@function_tool
def list_todos(show_completed: bool = False, priority: str = None) -> Dict[str, Any]:
    todos = load_todos()
    filtered = [todo for todo in todos 
                if (show_completed or not todo['completed']) and 
                (not priority or todo.get('priority') == priority)]
    return {"count": len(filtered), "todos": filtered}

@function_tool
def add_todo(
    title: str, 
    description: str = "", 
    due_date: str = "",
    priority: str = "medium"
) -> Dict[str, Any]:
    if not title.strip():
        return {"error": "Title cannot be empty"}
    
    try:
        if due_date:
            datetime.strptime(due_date, "%Y-%m-%d")
    except ValueError:
        return {"error": "Invalid date format. Use YYYY-MM-DD"}
    
    todos = load_todos()
    new_todo = {
        "id": len(todos) + 1,
        "title": title,
        "description": description,
        "completed": False,
        "due_date": due_date,
        "priority": priority.lower(),
        "created_at": datetime.now().isoformat()
    }
    
    todos.append(new_todo)
    save_todos(todos)
    return new_todo

@function_tool
def complete_todo(todo_id: int) -> Dict[str, Any]:
    todos = load_todos()
    for todo in todos:
        if todo['id'] == todo_id:
            todo['completed'] = True
            todo['completed_at'] = datetime.now().isoformat()
            save_todos(todos)
            return todo
    return {"error": f"Todo with ID {todo_id} not found"}

def _get_upcoming_todos(days_ahead: int = 3) -> Dict[str, Any]:
    todos = load_todos()
    upcoming = []
    today = datetime.now()
    
    for todo in todos:
        if todo.get('due_date') and not todo['completed']:
            try:
                due_date = datetime.strptime(todo['due_date'], "%Y-%m-%d")
                if due_date <= today + timedelta(days=days_ahead):
                    upcoming.append(todo)
            except ValueError:
                continue
                
    return {"count": len(upcoming), "todos": upcoming}

@function_tool
def get_upcoming_todos(days_ahead: int = 3) -> Dict[str, Any]:
    return _get_upcoming_todos(days_ahead)

# Updated agent with JSON-only instruction
agent = Agent(
    name="Advanced Todos Assistant",
    instructions=(
        "You are a sophisticated todo management system. "
        "Respond in valid JSON format only. Do not use natural language unless asked. "
        "You handle tasks with priority, due dates, and smart tracking."
    ),
    model=OpenAIChatCompletionsModel(model="gemini-2.0-flash", openai_client=client),
    tools=[list_todos, add_todo, complete_todo, get_upcoming_todos],
)

# --- Streamlit UI ---
st.set_page_config(page_title="Advanced Todos Assistant", layout="centered")
st.title("🚀 Advanced Todos Assistant")
st.markdown("""
**Features:**
- Prioritization (high/medium/low)
- Due date tracking
- Upcoming reminders
- Smart completion tracking
- Advanced search filters
""")

# Sidebar
with st.sidebar:
    st.header("Quick Actions")
    if st.button("🔄 Refresh All Todos"):
        st.rerun()
    if st.button("📅 Show Upcoming"):
        with st.spinner("Checking upcoming todos..."):
            output = _get_upcoming_todos()
            st.json(output)

# Main interface
col1, col2 = st.columns([3, 2])

with col1:
    st.subheader("💬 Chat with Assistant")
    user_query = st.text_input("Enter your query:", placeholder="E.g., 'Add high priority task to fix bug by tomorrow'")
    
    if st.button("Submit") and user_query.strip():
        with st.spinner("🧠 Processing..."):
            async def run_agent():
                result = await Runner.run(agent, user_query)
                return result.final_output

            try:
                output = asyncio.run(run_agent())
                st.success("🤖 Assistant Response:")

                if isinstance(output, dict):
                    st.json(output)
                    if "error" not in output:
                        st.rerun()
                else:
                    st.write(output)

            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

with col2:
    st.subheader("📋 Current Todos")
    todos = load_todos()
    
    if todos:
        for todo in todos:
            with st.container(border=True):
                cols = st.columns([1, 4])
                cols[0].checkbox(
                    "Done" if todo['completed'] else "Pending",
                    value=todo['completed'],
                    key=f"check_{todo['id']}",
                    disabled=True
                )
                cols[1].write(f"**{todo['title']}**")
                cols[1].caption(f"Priority: {todo.get('priority', 'medium').upper()}")
                if todo.get('due_date'):
                    cols[1].caption(f"📅 Due: {todo['due_date']}")
                if todo.get('description'):
                    cols[1].write(todo['description'])
    else:
        st.info("No todos found. Add one using the chat interface!")

st.subheader("⏳ Upcoming Deadlines")
upcoming = _get_upcoming_todos()["todos"]
if upcoming:
    for todo in upcoming:
        st.write(f"• {todo['title']} (Due: {todo['due_date']})")
else:
    st.info("No upcoming deadlines - good job!")
