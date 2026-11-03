import operator 
from typing import Annotated, TypedDict

from langgraph.graph import StateGraph, START, END


class ResearchState(TypedDict):
    topic: str
    sources: Annotated[list[str], operator.add]
    summary: str


def web_research(state: ResearchState):
    print("Searching the web...")
    return {
        "sources": [f"Web source about {state['topic']}"]
    }


def paper_research(state: ResearchState):
    print("Searching research papers...")
    return {
        "sources": [f"Research paper about {state['topic']}"]
    }


def summarize(state: ResearchState):
    print("Combining sources...")
    summary = " | ".join(state["sources"])
    return {"summary": summary}


builder = StateGraph(ResearchState)

builder.add_node("web", web_research)
builder.add_node("papers", paper_research)
builder.add_node("summarize", summarize)

builder.add_edge(START, "web")
builder.add_edge(START, "papers")

# Both branches must complete before summarization.
builder.add_edge("web", "summarize")
builder.add_edge("papers", "summarize")

builder.add_edge("summarize", END)

graph = builder.compile()

result = graph.invoke({
    "topic": "LangGraph",
    "sources": [],
    "summary": ""
})

print("\nFinal state:")
print(result)

'''
A reducer is useful when multiple updates need to be combined into the same state field.

If two nodes update different keys, you don't need a reducer for those keys:
```python
# Node A
return {"word_count": 42}

# Node B
return {"keywords": ["graph", "agent"]}
```

'''