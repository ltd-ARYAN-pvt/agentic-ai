from typing import TypedDict
from langgraph.graph import StateGraph, START, END


class MathState(TypedDict):
    number: int
    result: int
    message: str


def double(state: MathState):
    print("Running double node...")
    return {"number": state["number"] * 2}


def add_five(state: MathState):
    print("Running add_five node...")
    return {"result": state["number"] + 5}


def format_result(state: MathState):
    print("Running format_result node...")
    return {"message": f"Final answer: {state['result']}"}


builder = StateGraph(MathState)

builder.add_node("double", double)
builder.add_node("add_five", add_five)
builder.add_node("format_result", format_result)

builder.add_edge(START, "double")
builder.add_edge("double", "add_five")
builder.add_edge("add_five", "format_result")
builder.add_edge("format_result", END)

graph = builder.compile()

initial_state = {
    "number": 10,
    "result": 0,
    "message": ""
}

print("\n--- INVOKE ---")
result = graph.invoke(initial_state)
print("Final:", result)

print("\n--- STREAM: UPDATES ---")
for update in graph.stream(initial_state, stream_mode="updates"):
    print(update)

print("\n--- STREAM: VALUES ---")
for state in graph.stream(initial_state, stream_mode="values"):
    print(state)