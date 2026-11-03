from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.store.memory import InMemoryStore


# Short-term memory: conversation checkpoints
checkpointer = InMemorySaver()

# Long-term memory: shared facts
store = InMemoryStore()


def assistant(state: MessagesState, config, *, store):
    # A shared user identity lets different threads access
    # the same user's long-term memories.
    user_id = config["configurable"].get("user_id", "user-1")
    namespace = ("users", user_id, "memories")

    last_message = state["messages"][-1]
    text = str(last_message.content).strip()
    lower_text = text.lower()

    # Example memory-writing logic.
    # This is intentionally simple string matching.
    prefix = "my favorite color is "

    if lower_text.startswith(prefix):
        color = text[len(prefix):].strip(" .!?")

        store.put(
            namespace,
            "favorite_color",
            {"color": color}
        )

        reply = f"I'll remember that your favorite color is {color}."

    elif "favorite color" in lower_text:
        # Retrieve a fact from long-term memory.
        item = store.get(namespace, "favorite_color")

        if item:
            color = item.value["color"]
            reply = f"Your favorite color is {color}."
        else:
            reply = "I don't know your favorite color yet."

    else:
        reply = "Tell me something about yourself!"

    return {"messages": [AIMessage(content=reply)]}


builder = StateGraph(MessagesState)
builder.add_node("assistant", assistant)
builder.add_edge(START, "assistant")
builder.add_edge("assistant", END)

graph = builder.compile(
    checkpointer=checkpointer,
    store=store
)


# Same user, first conversation
chat_1 = {
    "configurable": {
        "thread_id": "chat-1",
        "user_id": "user-1"
    }
}

result_1 = graph.invoke(
    {"messages": [
        HumanMessage(content="My favorite color is blue.")
    ]},
    config=chat_1
)

print("Chat 1:", result_1["messages"][-1].content)


# Same user, entirely different conversation thread
chat_2 = {
    "configurable": {
        "thread_id": "chat-2",
        "user_id": "user-1"
    }
}

result_2 = graph.invoke(
    {"messages": [
        HumanMessage(content="What is my favorite color?")
    ]},
    config=chat_2
)

print("Chat 2:", result_2["messages"][-1].content)

# different user, entirely different conversation thread
chat_3 = {
    "configurable": {
        "thread_id": "chat-3",
        "user_id": "user-2"
    }
}

result_2 = graph.invoke(
    {"messages": [
        HumanMessage(content="My favorite color is red")
    ]},
    config=chat_2
)

print("Chat 2:", result_2["messages"][-1].content)
# different user, entirely different conversation thread
chat_4 = {
    "configurable": {
        "thread_id": "chat-4",
        "user_id": "user-2"
    }
}

result_2 = graph.invoke(
    {"messages": [
        HumanMessage(content="What is my favorite color?")
    ]},
    config=chat_2
)

print("Chat 2:", result_2["messages"][-1].content)