
from langchain_core.tools import tool
from langchain_ollama import ChatOllama
from utils import getmodel


@tool
def multiply(a: int, b: int) -> int:
    """Multiply two integers and return the result."""
    return a * b


llm = ChatOllama(
    model=getmodel(),
    temperature=0,
)

tools = [multiply]
llm_with_tools = llm.bind_tools(tools)

response = llm_with_tools.invoke(
    "Use the multiply tool to calculate 18742 multiplied by 9361."
)

print("LLM content:", response.content)
print("Requested tool calls:", response.tool_calls)

# Execute the tool calls requested by the LLM
for tool_call in response.tool_calls:
    selected_tool = next(
        tool for tool in tools if tool.name == tool_call["name"]
    )

    result = selected_tool.invoke(tool_call["args"])

    print(f"\nTool executed: {tool_call['name']}")
    print(f"Tool result: {result}")