from langgraph.graph import StateGraph, START , END #type: ignore
from typing_extensions import TypedDict #type: ignore
from typing import Literal 
import random

class State(TypedDict):
    graph_state: str


def node_1(state):
    print("Node 1: Starting the process.", state["graph_state"])
    return {"graph_state": state["graph_state"] + " I am "}
def node_2(state):
    print("Node 2: Continuing the process. ", state["graph_state"])
    return {"graph_state": state["graph_state"] + " happy"}
def node_3(state):
    print("Node 3: Finalizing the process, ", state["graph_state"])
    return {"graph_state": state["graph_state"] + " sad"}

def decide_mode(state) -> Literal["node_2", "node_3"]:
    # user_input = state["graph_state"]
    # print("decide mode state input is ", user_input)
    if random.random() < 0.5:
        return "node_2"
    return "node_3"


builder = StateGraph(State)

builder.add_node("node_1", node_1)
builder.add_node("node_2", node_2)
builder.add_node("node_3", node_3)

builder.add_edge(START, "node_1")
builder.add_conditional_edges("node_1", decide_mode)
builder.add_edge("node_2", END)
builder.add_edge("node_3", END)

graph = builder.compile()

output = graph.invoke({"graph_state" : "Hi, this is Danish"})

print("Final output is " , output)