from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain_ollama import ChatOllama
from utils import getmodel


@tool
def multiply(a: int, b: int) -> int:
    """Multiply two integers and return the result."""
    return a * b


@tool
def add(a: int, b: int) -> int:
    """Add two integers and return the result."""
    return a + b


llm = ChatOllama(
    model=getmodel(),
    temperature=0,
)

agent = create_agent(
    model=llm,
    tools=[multiply, add],
    system_prompt=(
        "You are a helpful assistant. "
        "Use tools when appropriate. "
        "Use the actual result returned by a tool "
        "when performing dependent calculations."
    ),
)

result = agent.invoke({
    "messages": [
        {
            "role": "user",
            "content": "What is 125 plus 100? and multiply 125 to the result too",
        }
    ]
})

for message in result["messages"]:
    print(type(message).__name__, ":", message.content)

print("\nFinal answer:", result["messages"][-1].content)