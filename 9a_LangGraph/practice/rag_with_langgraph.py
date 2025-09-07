import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.tools.retriever import create_retriever_tool
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver
from typing import Annotated
from typing_extensions import TypedDict
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
import uuid

# 1. Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
print("gemini api key is ", GEMINI_API_KEY)

# 2. Load and process the PDF book
pdf_path = os.path.join(os.path.dirname(__file__), "my_book.pdf")

# Check if PDF exists
if not os.path.exists(pdf_path):
    print(f"ERROR: PDF file not found at {pdf_path}")
    exit(1)

print(f"Loading PDF from: {pdf_path}")
loader = PyPDFLoader(pdf_path)
docs = loader.load()

print(f"Loaded {len(docs)} pages from PDF")

# Debug: Check if documents have content
if not docs:
    print("ERROR: No documents loaded from PDF")
    exit(1)

# Print first few characters of first document for debugging
print(f"First document preview: {docs[0].page_content[:200]}...")

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
documents = text_splitter.split_documents(docs)

print(f"Split into {len(documents)} chunks")

# Debug: Check if chunks have content
if not documents:
    print("ERROR: No chunks created from documents")
    exit(1)

print(f"First chunk preview: {documents[0].page_content[:200]}...")

# 3. Create or load vector store and retriever
faiss_path = "practice/faiss_index"
if os.path.exists(faiss_path):
    print("Loading existing FAISS index...")
    try:
        vector = FAISS.load_local(
            faiss_path,
            GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=GEMINI_API_KEY),
            allow_dangerous_deserialization=True
        )
    except Exception as e:
        print(f"Error loading FAISS index: {e}")
        print("Creating new FAISS index...")
        vector = FAISS.from_documents(
            documents, GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=GEMINI_API_KEY)
        )
        vector.save_local(faiss_path)
else:
    print("Creating new FAISS index (this may take a while)...")
    vector = FAISS.from_documents(
        documents, GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=GEMINI_API_KEY)
    )
    vector.save_local(faiss_path)

# Test retriever
retriever = vector.as_retriever(search_kwargs={"k": 5})  # Get top 5 results
print("Testing retriever...")
test_results = retriever.invoke("introduction")  # Updated to use invoke instead of deprecated method
print(f"Test retrieval returned {len(test_results)} documents")
for i, doc in enumerate(test_results):
    print(f"Result {i+1}: {doc.page_content[:100]}...")

retriever_tool = create_retriever_tool(
    retriever,
    "book_search",
    "Search for information in the book about Agentic AI. Use this tool to find relevant content from the book before answering any questions."
)

# 4. Set up Gemini LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash", 
    google_api_key=GEMINI_API_KEY,
    temperature=0.1  # Make responses more deterministic
)

# 5. More explicit prompt template with stronger instructions
primary_assistant_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            '''You are a helpful assistant that answers questions about a book on Agentic AI.

MANDATORY RULES - YOU MUST FOLLOW THESE:
1. For EVERY question about the book, you MUST use the book_search tool first
2. NEVER provide answers without first searching the book
3. You have access to a book_search tool - use it for every question
4. After getting results from book_search, provide a comprehensive answer based on the retrieved content
5. If the search doesn't return relevant information, say "I couldn't find specific information about this topic in the book"

WORKFLOW:
1. User asks question → Use book_search tool
2. Get results → Provide answer based on results
3. Always cite the book content in your response

You MUST use the book_search tool for every question. Do not skip this step.''',
        ),
        ("placeholder", "{messages}"),
    ]
)

# 6. Tool list
tools = [retriever_tool]

from langgraph.graph.message import AnyMessage, add_messages

class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]

def should_continue(state: State):
    """Check if we should continue to tools or end"""
    last_message = state["messages"][-1]
    print(f"Checking if should continue. Last message type: {type(last_message)}")
    
    # If the last message is from AI and has tool calls, go to tools
    if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
        print(f"AI message has tool calls: {len(last_message.tool_calls)}")
        return "tools"
    
    # Otherwise, end
    print("No tool calls found, ending")
    return END

def call_model(state: State):
    """Call the model with the current state"""
    print(f"Calling model with {len(state['messages'])} messages")
    
    # Check if this is the first user message and no tool has been called yet
    user_messages = [msg for msg in state['messages'] if isinstance(msg, HumanMessage)]
    tool_messages = [msg for msg in state['messages'] if isinstance(msg, ToolMessage)]
    
    print(f"User messages: {len(user_messages)}, Tool messages: {len(tool_messages)}")
    
    # If we have a user question but no tool results yet, force tool use
    if user_messages and not tool_messages:
        print("Forcing tool use for user question")
        # Create a more explicit prompt to force tool usage
        enhanced_messages = state['messages'].copy()
        if isinstance(enhanced_messages[-1], HumanMessage):
            enhanced_messages[-1] = HumanMessage(
                content=f"Use the book_search tool to find information about: {enhanced_messages[-1].content}"
            )
        
        # Create the chain properly
        chain = primary_assistant_prompt | llm.bind_tools(tools)
        result = chain.invoke({"messages": enhanced_messages})
    else:
        # Create the chain properly
        chain = primary_assistant_prompt | llm.bind_tools(tools)
        result = chain.invoke(state)
    
    print(f"Model response type: {type(result)}")
    if hasattr(result, 'tool_calls') and result.tool_calls:
        print(f"Model wants to call {len(result.tool_calls)} tools")
        for tool_call in result.tool_calls:
            print(f"Tool call: {tool_call['name']} with args: {tool_call['args']}")
    else:
        print(f"Model response (no tool calls): {result.content[:100]}...")
    
    return {"messages": [result]}

# Alternative approach: Create a custom function that forces tool use
def force_search_and_answer(state: State):
    """Force the model to search first, then answer"""
    print("Forcing search and answer approach")
    
    # Get the last human message
    last_human_msg = None
    for msg in reversed(state['messages']):
        if isinstance(msg, HumanMessage):
            last_human_msg = msg
            break
    
    if not last_human_msg:
        return {"messages": [AIMessage(content="I need a question to answer.")]}
    
    # First, search the book
    print("Step 1: Searching the book...")
    search_results = retriever.invoke(last_human_msg.content)
    print(f"Found {len(search_results)} relevant documents")
    
    # Create context from search results
    context = "\n\n".join([doc.page_content for doc in search_results])
    
    # Create a focused prompt for answering
    answer_prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert on Agentic AI. Based on the book content provided below, answer the user's question comprehensively.

Book Content:
{context}

Instructions:
- Answer based only on the provided book content
- Be comprehensive and detailed
- If the book content doesn't contain relevant information, say so
- Quote relevant parts of the book when appropriate"""),
        ("human", "{question}")
    ])
    
    # Generate answer
    chain = answer_prompt | llm
    result = chain.invoke({
        "context": context,
        "question": last_human_msg.content
    })
    
    print(f"Generated answer: {result.content[:100]}...")
    
    return {"messages": [result]}

# 7. Build the graph with alternative approach
builder = StateGraph(State)

# Add nodes
builder.add_node("agent", call_model)
builder.add_node("tools", ToolNode(tools))
builder.add_node("search_and_answer", force_search_and_answer)  # Alternative approach

# Add edges
builder.add_edge(START, "agent")
builder.add_conditional_edges("agent", should_continue)
builder.add_edge("tools", "agent")

# Compile with memory
memory = MemorySaver()
graph = builder.compile(checkpointer=memory)

# Alternative simpler graph that forces search
def create_simple_graph():
    """Create a simpler graph that always searches first"""
    simple_builder = StateGraph(State)
    simple_builder.add_node("search_and_answer", force_search_and_answer)
    simple_builder.add_edge(START, "search_and_answer")
    simple_builder.add_edge("search_and_answer", END)
    return simple_builder.compile()

# Use the simpler approach
simple_graph = create_simple_graph()

if __name__ == "__main__":
    config = {
        "configurable": {
            "thread_id": str(uuid.uuid4()),
        }
    }
    
    print("=" * 50)
    print("Book QA System Ready!")
    print("=" * 50)
    print("Ask questions about your book! (Type 'exit' to quit)")
    print("Using simplified approach that always searches the book first.")
    
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() in ["exit", "quit"]:
            break
        
        print(f"\nProcessing question: {user_input}")
        print("-" * 30)
        
        try:
            # Create a fresh conversation for each question
            fresh_config = {
                "configurable": {
                    "thread_id": str(uuid.uuid4()),
                }
            }
            
            # Use the simple graph that always searches
            result = simple_graph.invoke(
                {"messages": [HumanMessage(content=user_input)]}, 
                fresh_config
            )
            
            print(f"\nGraph execution completed. Total messages: {len(result['messages'])}")
            
            # Find the final AI response
            final_response = None
            for msg in reversed(result["messages"]):
                if isinstance(msg, AIMessage):
                    final_response = msg
                    break
            
            if final_response:
                print(f"\nAssistant: {final_response.content}")
            else:
                print("\nNo final response found")
                
        except Exception as e:
            print(f"Error processing question: {e}")
            import traceback
            traceback.print_exc()
    
    print("\nTo use the original complex graph instead, replace 'simple_graph' with 'graph' in the invoke call.")