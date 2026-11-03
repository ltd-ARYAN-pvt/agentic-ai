from typing import TypedDict

from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, START, END
from utils import get_model


class ChatState(TypedDict):
    question: str
    answer: str


llm = ChatOllama(
    model=get_model(),
    temperature=0,
)


# def generate_answer(state: ChatState):
#     response = llm.invoke(state["question"])
#     return {"answer": response.content}

def generate_answer(state: ChatState):
    answer = ""

    for chunk in llm.stream(state["question"]):
        answer += chunk.content

    return {"answer": answer}


builder = StateGraph(ChatState)

builder.add_node("generate", generate_answer)
builder.add_edge(START, "generate")
builder.add_edge("generate", END)

graph = builder.compile()

# Normal execution
# result = graph.invoke({
#     "question": "Explain Agentic Ai in two sentences.",
#     "answer": "",
# })

# print("Complete answer:", result["answer"])

print("Answer: ", end="", flush=True)

for chunk, metadata in graph.stream(
    {
        "question": "Explain Langchain in two sentences.",
        "answer": "",
    },
    stream_mode="messages",
):
    if chunk.content:
        print(chunk.content, end="", flush=True)

print()