from typing import TypedDict, Literal
from langgraph.graph import StateGraph, START, END


# Step 1: Shared state
class ResearchState(TypedDict):
    score: int
    attempts: int
    status: str


# Step 2: Research node
def research(state: ResearchState):
    attempt = state["attempts"] + 1

    # Simulate improving research quality
    score = min(state["score"] + 3, 10)

    print(f"Research attempt {attempt}: score = {score}")

    return {
        "score": score,
        "attempts": attempt
    }


# Step 3: Evaluate node
def evaluate(state: ResearchState):
    print(f"Evaluating score: {state['score']}")
    return {}


# Step 4: Decide where to go next
def route_quality(
    state: ResearchState
) -> Literal["research", "finish", "stop"]:

    if state["score"] >= 7:
        return "finish"

    if state["attempts"] >= 3:
        return "stop"

    return "research"


# Step 5: Terminal nodes
def finish(state: ResearchState):
    return {"status": "Research quality accepted!"}


def stop(state: ResearchState):
    return {"status": "Stopped: maximum attempts reached."}


# Step 6: Build the graph
builder = StateGraph(ResearchState)

builder.add_node("research", research)
builder.add_node("evaluate", evaluate)
builder.add_node("finish", finish)
builder.add_node("stop", stop)

builder.add_edge(START, "research")
builder.add_edge("research", "evaluate")

builder.add_conditional_edges(
    "evaluate",
    route_quality
)

builder.add_edge("finish", END)
builder.add_edge("stop", END)

graph = builder.compile()


# Step 7: Run it
result = graph.invoke({
    "score": -2,
    "attempts": 0,
    "status": ""
})

print("\nFinal state:", result)