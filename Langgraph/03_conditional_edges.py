from typing import TypedDict, Literal
from langgraph.graph import StateGraph, START, END

#-->Step-1 Define Shared State
class NumberState(TypedDict):
    number:int
    results:str

#-->Step-2 Define Nodes
def high_node(state: NumberState):
    return {"results": "Number is high"}

def medium_node(state: NumberState):
    return {"results": "Number is medium"}

def low_node(state: NumberState):
    return {"results": "Number is low"}

#--> Step-3 Define Conditional Node and edge
def check_number(state: NumberState):
    print(f"Checking number: {state['number']}")
    return {}

def route_info(state: NumberState) -> Literal['high', 'mid', 'low']:
    if state["number"]>10:
        return "high"
    elif state["number"]>=8:
        return "mid"
    else:
        return "low"

#--> Step-4 Define Graph
builder = StateGraph(NumberState)

builder.add_node("check",check_number)
builder.add_node("low",low_node)
builder.add_node("high",high_node)
builder.add_node("mid",medium_node)

builder.add_edge(START, "check")
builder.add_conditional_edges("check",route_info)
builder.add_edge("low",END)
builder.add_edge("mid",END)
builder.add_edge("high",END)

graph=builder.compile()

#--> Step-5 Invoke the graph
result = graph.invoke({
    "number":1,
    "results":""
})

print(result)