from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.checkpoint.memory import InMemorySaver


def assistant(state: MessagesState):
    messages = state["messages"]

    # Look for a color mentioned earlier in the conversation
    known_color = None

    for message in messages:
        if isinstance(message, HumanMessage):
            text = message.content.lower()
            if "favorite color is " in text:
                known_color = text.split("favorite color is ", 1)[1].strip(" .!?")

    last_message = messages[-1].content.lower()

    if "favorite color" in last_message and known_color:
        reply = f"Your favorite color is {known_color}."
    else:
        reply = "Tell me something about yourself!"

    return {"messages": [AIMessage(content=reply)]}


builder = StateGraph(MessagesState)
builder.add_node("assistant", assistant)
builder.add_edge(START, "assistant")
builder.add_edge("assistant", END)

graph = builder.compile(checkpointer=InMemorySaver())

config1 = {"configurable": {"thread_id": "chat-1"}}

# First interaction
graph.invoke(
    {"messages": [HumanMessage(content="My favorite color is blue.")]},
    config=config1,
)

# Second interaction: same thread
result = graph.invoke(
    {"messages": [HumanMessage(content="What is my favorite color?")]},
    config=config1,
)

print(result["messages"][-1].content)

# Third interaction: different thread
config2 = {"configurable": {"thread_id": "chat-2"}}

result = graph.invoke(
    {"messages": [HumanMessage(content="What is my favorite color?")]},
    config=config2,
)

print(result["messages"][-1].content)

