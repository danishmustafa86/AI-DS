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
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")

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
test_results = retriever.get_relevant_documents("introduction")
print(f"Test retrieval returned {len(test_results)} documents")
for i, doc in enumerate(test_results):
    print(f"Result {i+1}: {doc.page_content[:100]}...")

retriever_tool = create_retriever_tool(
    retriever,
    "Book_Knowledge",
    "Search for information in the provided book. Use this tool to find relevant content from the book."
)

# 4. Set up Gemini LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash", 
    google_api_key=GEMINI_API_KEY,
    temperature=0.1  # Make responses more deterministic
)

# 5. More explicit prompt template
primary_assistant_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            '''You are a helpful assistant that answers questions about a specific book.

CRITICAL INSTRUCTIONS:
1. For ANY question about the book content, you MUST first use the Book_Knowledge tool to search for relevant information
2. NEVER answer questions about the book without using the Book_Knowledge tool first
3. After using the tool, provide a comprehensive answer based on the retrieved content
4. If the tool doesn't return relevant information, say "I couldn't find specific information about this topic in the book"
5. Always base your answers on the retrieved content, not your general knowledge

Remember: Always use the Book_Knowledge tool first for any book-related question!''',
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

# 7. Build the graph
builder = StateGraph(State)

# Add nodes
builder.add_node("agent", call_model)
builder.add_node("tools", ToolNode(tools))

# Add edges
builder.add_edge(START, "agent")
builder.add_conditional_edges("agent", should_continue)
builder.add_edge("tools", "agent")

# Compile with memory
memory = MemorySaver()
graph = builder.compile(checkpointer=memory)

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
    
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() in ["exit", "quit"]:
            break
        
        print(f"\nProcessing question: {user_input}")
        print("-" * 30)
        
        try:
            # Create a fresh conversation for each question to avoid confusion
            fresh_config = {
                "configurable": {
                    "thread_id": str(uuid.uuid4()),
                }
            }
            
            result = graph.invoke(
                {"messages": [HumanMessage(content=user_input)]}, 
                fresh_config
            )
            
            print(f"\nGraph execution completed. Total messages: {len(result['messages'])}")
            
            # Find the final AI response
            final_response = None
            for msg in reversed(result["messages"]):
                if isinstance(msg, AIMessage) and not (hasattr(msg, 'tool_calls') and msg.tool_calls):
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