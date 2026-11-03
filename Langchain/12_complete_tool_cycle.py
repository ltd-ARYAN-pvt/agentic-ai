from langchain_core.tools import tool
from langchain_core.messages import ToolMessage
from langchain_ollama import ChatOllama
from utils import getmodel


@tool
def multiply(a: int, b: int) -> int:
    """Multiply two integers and return the result."""
    return a * b


tools = [multiply]
tools_by_name = {tool.name: tool for tool in tools}

llm = ChatOllama(
    model=getmodel(),
    temperature=0,
)

llm_with_tools = llm.bind_tools(tools)

# Step 1: Start the conversation
messages = [
    (
        "user",
        "Use the multiply tool to calculate 18742 multiplied by 9361. "
        "Then explain the result briefly.",
    )
]

# Step 2: Ask the LLM
ai_message = llm_with_tools.invoke(messages)
messages.append(ai_message)

# Step 3: Execute any requested tools
for tool_call in ai_message.tool_calls:
    selected_tool = tools_by_name[tool_call["name"]]

    result = selected_tool.invoke(tool_call["args"])

    print(f"Tool executed: {tool_call['name']}")
    print(f"Tool result: {result}")

    # Step 4: Send the result back to the LLM
    messages.append(
        ToolMessage(
            content=str(result),
            tool_call_id=tool_call["id"],
        )
    )

# Step 5: Ask the LLM to produce the final answer
final_response = llm_with_tools.invoke(messages)

print("\nFinal answer:")
print(final_response.content)
print(messages)