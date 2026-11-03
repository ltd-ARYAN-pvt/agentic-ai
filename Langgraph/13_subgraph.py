
import operator
from typing import Annotated, TypedDict

from langgraph.graph import StateGraph, START, END


# Shared state schema
class ResearchState(TypedDict):
    topic: str
    sources: Annotated[list[str], operator.add]
    summary: str
    final_answer: str


# ---------------------------------
# 1. Build the research subgraph
# ---------------------------------

def web_research(state: ResearchState):
    print("Research subgraph: searching web...")
    return {
        "sources": [f"Web source about {state['topic']}"]
    }


def paper_research(state: ResearchState):
    print("Research subgraph: searching papers...")
    return {
        "sources": [f"Paper about {state['topic']}"]
    }


def combine_findings(state: ResearchState):
    print("Research subgraph: combining findings...")
    return {
        "summary": " | ".join(state["sources"])
    }


research_builder = StateGraph(ResearchState)

research_builder.add_node("web", web_research)
research_builder.add_node("papers", paper_research)
research_builder.add_node("combine", combine_findings)

research_builder.add_edge(START, "web")
research_builder.add_edge(START, "papers")
research_builder.add_edge("web", "combine")
research_builder.add_edge("papers", "combine")
research_builder.add_edge("combine", END)

research_graph = research_builder.compile()


# ---------------------------------
# 2. Build the parent graph
# ---------------------------------

def create_final_answer(state: ResearchState):
    return {
        "final_answer": (
            f"Research topic: {state['topic']}\n"
            f"Findings: {state['summary']}"
        )
    }


parent_builder = StateGraph(ResearchState)

# The compiled subgraph becomes a node!
parent_builder.add_node("research", research_graph)
parent_builder.add_node("finalize", create_final_answer)

parent_builder.add_edge(START, "research")
parent_builder.add_edge("research", "finalize")
parent_builder.add_edge("finalize", END)

parent_graph = parent_builder.compile()


# ---------------------------------
# 3. Run the parent graph
# ---------------------------------

result = parent_graph.invoke({
    "topic": "LangGraph",
    "sources": [],
    "summary": "",
    "final_answer": "",
})

print("\nFINAL ANSWER:")
print(result["final_answer"])