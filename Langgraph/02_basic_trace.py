from typing import TypedDict
from langgraph.graph import StateGraph, START, END

#--> State
class NumberState(TypedDict):
    number: int
    message: str

#--> Nodes
def double(state: NumberState):
    result = state["number"] * 2
    print("Node 1:", result)
    return {"number": result}


def add_three(state: NumberState):
    result = state["number"] + 3
    print("Node 2:", result)
    return {"number": result}


def format_result(state: NumberState):
    message = f"Final result: {state['number']}"
    print("Node 3:", message)
    return {"message": message}

#--> Graph and Edges
builder = StateGraph(NumberState)

builder.add_node("double", double)
builder.add_node("add_three", add_three)
builder.add_node("format", format_result)

builder.add_edge(START, "double")
builder.add_edge("double", "add_three")
builder.add_edge("add_three", "format")
builder.add_edge("format", END)

graph = builder.compile()

result = graph.invoke({
    "number": 5,
    "message": ""
})

print("\nFinal state:", result)