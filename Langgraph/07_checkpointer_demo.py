from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver

class CounterState(TypedDict):
    count: int

def increment(state: CounterState):
    print("Incrementing...")
    return {"count": state["count"] + 1}

builder = StateGraph(CounterState)

builder.add_node("increment", increment)
builder.add_edge(START, "increment")
builder.add_edge("increment", END)

# Save graph checkpoints in memory
checkpointer = InMemorySaver()

graph = builder.compile(checkpointer=checkpointer)

# Every conversation/workflow needs a thread identifier
config = {"configurable": {"thread_id": "demo-1"}}

# First execution
result1 = graph.invoke({"count": 0}, config=config)
print("First result:", result1)

# Read the latest saved state for this thread
saved_state = graph.get_state(config)
print("Saved state:", saved_state.values)