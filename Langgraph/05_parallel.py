from typing import TypedDict
from langgraph.graph import StateGraph, START, END

class DocumentState(TypedDict):
    text: str
    word_count: int
    keywords: list[str]


def count_words(state: DocumentState):
    return {
        "word_count": len(state["text"].split())
    }


def find_keywords(state: DocumentState):
    words = state["text"].lower().split()
    keywords = [
        word for word in words
        if word.strip(".,!?") in {"python", "langgraph", "ai"}
    ]
    return {"keywords": keywords}


builder = StateGraph(DocumentState)

builder.add_node("count", count_words)
builder.add_node("keywords", find_keywords)

builder.add_edge(START, "count")
builder.add_edge(START, "keywords")

builder.add_edge("count", END)
builder.add_edge("keywords", END)

graph = builder.compile()

result = graph.invoke({
    "text": "Python and LangGraph help build AI agents",
    "word_count": 0,
    "keywords": []
})

print(result)