from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, MessagesState
from langgraph.prebuilt import ToolNode, tools_condition
from utils import get_model


# 1. Define a tool
@tool
def multiply(a: float, b: float) -> float:
    """Multiply two integers and return the result."""
    print("Multiplication tool used.....")
    return a * b

@tool
def divide(a: float, b: float) -> float | str:
    """Divide two numbers and return the result."""
    print("Division tool used.....")
    #--> Type 1 Error handling
    if b == 0:
        raise ValueError("Cannot divide by zero.")
    return a / b

@tool
def add(a: float, b: float) -> float:
    """Add two numbers and return the result. Subtract two numbers by using a + (-b) property"""
    print("Addition tool used.....")
    return a + b


# 2. Create the model and bind available tools
tools = [multiply,divide,add]

llm = ChatOllama(
    model=get_model(),
    temperature=0,
).bind_tools(tools)


# 3. Create the assistant node
def assistant(state: MessagesState):
    response = llm.invoke(state["messages"])
    print("\n--- ASSISTANT DEBUG ---")
    print("Content:", repr(response.content))
    print("Tool calls:", response.tool_calls)
    print("Invalid tool calls:", response.invalid_tool_calls) 
    return {"messages": [response]}


# 4. Build the graph
builder = StateGraph(MessagesState)

#--> Type-2 Exception Handling using ToolNode
tool_node = ToolNode(
    tools=tools,
    handle_tool_errors=True,
)

builder.add_node("assistant", assistant)
builder.add_node("tools", tool_node)

builder.add_edge(START, "assistant")

# Choose whether to call a tool or finish
builder.add_conditional_edges(
    "assistant",
    tools_condition,
)

# After executing a tool, ask the LLM what to do next
builder.add_edge("tools", "assistant")

graph = builder.compile()


# 5. Run the agent
result = graph.invoke({
    "messages": [
        SystemMessage(content="""
You are a calculation assistant.

You have multiply, divide, and add tools.
For every arithmetic operation requested, call the
appropriate tool. Do not write JSON representations
of tool calls as ordinary text.

Execute the operations in the order requested.
Use the actual result from each tool in the next call.
Do not calculate the result yourself when a tool is available.
After all operations are complete, report the final result.
"""),
        HumanMessage(content=(
            "Multiple 2314 with 1001. divide the result with 0. What is the final result?"
        )),
    ]
})

print(result["messages"][-1].content)