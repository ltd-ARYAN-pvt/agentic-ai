from langchain_core.tools import tool
from langchain_core.messages import ToolMessage
from langchain_ollama import ChatOllama
from utils import getmodel


@tool
def multiply(a: int, b: int) -> int:
    """Multiply two integers."""
    return a * b


@tool
def add(a: int, b: int) -> int:
    """Add two integers."""
    return a + b


tools = [multiply, add]
tools_by_name = {t.name: t for t in tools}

llm = ChatOllama(
    model=getmodel(),
    temperature=0,
)

llm_with_tools = llm.bind_tools(tools)


def run_agent(question: str, max_iterations: int = 5) -> str:
    messages = [("user", question)]

    for iteration in range(max_iterations):
        ai_message = llm_with_tools.invoke(messages)
        messages.append(ai_message)

        # No more tool calls: return the final answer
        if not ai_message.tool_calls:
            return ai_message.content,messages

        for tool_call in ai_message.tool_calls:
            tool_name = tool_call["name"]

            if tool_name not in tools_by_name:
                raise ValueError(f"Unknown tool: {tool_name}")

            result = tools_by_name[tool_name].invoke(
                tool_call["args"]
            )

            print(f"Tool: {tool_name}")
            print(f"Result: {result}")

            messages.append(
                ToolMessage(
                    content=str(result),
                    tool_call_id=tool_call["id"],
                )
            )

    raise RuntimeError("Maximum tool-calling iterations reached.")


answer,messages = run_agent(
    "Calculate 27678 multiplied by 376, once multiplication is completed then add 65568 to result.\
    You MUST use the multiply tool for the multiplication\
    and the add tool for the addition.\
    Do not calculate either operation mentally."
)

print("\nFinal answer:", answer)
for msg in messages:
    print(msg)
    print("-"*50)