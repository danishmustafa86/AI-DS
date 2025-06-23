from langgraph.graph import StateGraph, START, END  #type: ignore
from typing_extensions import TypedDict #type: ignore
from typing import Literal
import random

class state(TypedDict):
    graph_state: str


def node_1(state):
    print("Node 1 is runing, current state is ", state["graph_state"])
    return {"graph_state": state["graph_state"] + " I am "}
def node_2 (state):
    print("node 2 is ruining, Current state is ", state["graph_state"])
    return {"graph_state": state["graph_state"] + "happy"}
def node_3(state):
    print("node 3 is running, current state is ", state['graph_state'])
    return {"graph_state": state["graph_state"] + "sad"}

def decide_node(state) -> Literal["node_2", "node_3"]:
    if random.random() < 0.5:
        return "node_3"
    return "node_3"

builder = StateGraph(state)

builder.add_node("node_1", node_1)
builder.add_node("node_3", node_3)
builder.add_node("node_2", node_2)

builder.add_edge(START, "node_1")
builder.add_conditional_edges("node_1", decide_node)
builder.add_edge("node_2", END)
builder.add_edge("node_3", END)

graph = builder.compile()

output = graph.invoke({"graph_state": "Hi, this is Danish"})

print("Final output is => ", output)
