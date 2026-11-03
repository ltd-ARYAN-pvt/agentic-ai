from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, START, END


# 1. Define our state schema
class TextState(BaseModel):
    text: str
    cleaned_text: str = ""
    word_count: int = Field(default=0, ge=0)


# 2. Define the nodes
def clean_text(state: TextState) -> dict:
    cleaned = state.text.strip()
    print(f"Cleaning: {state.text!r} -> {cleaned!r}")

    return {"cleaned_text": cleaned}


def analyze_text(state: TextState) -> dict:
    count = len(state.cleaned_text.split())
    print(f"Analyzing: {state.cleaned_text!r} -> {count} words")

    return {"word_count": count}


# 3. Build the graph
builder = StateGraph(TextState)

builder.add_node("clean", clean_text)
builder.add_node("analyze", analyze_text)

builder.add_edge(START, "clean")
builder.add_edge("clean", "analyze")
builder.add_edge("analyze", END)

# 4. Compile the graph
graph = builder.compile()

# 5. Run the workflow
result = graph.invoke({
    "text": "   Hello LangGraph, welcome buddy!   "
})

print("\nFinal result:")
print(result)