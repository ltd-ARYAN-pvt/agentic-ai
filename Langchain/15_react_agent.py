#--> ReAct = Reason then Act
from langgraph.prebuilt import create_react_agent
from langchain_ollama import ChatOllama
from langchain_core.tools import tool
from utils import getmodel

@tool
def multiply(a: int, b: int) -> int:
    """Multiply two integers."""
    return a * b

@tool
def add(a: int, b: int) -> int:
    """Add two integers and return the result."""
    return a + b

llm = ChatOllama(
    model=getmodel(),
    temperature=0
)

agent = create_react_agent(
    model=llm,
    tools=[multiply,add],
)

result = agent.invoke({
    "messages": [
        {"role": "user", "content": "What is result = 125 multiplied by 100? then result+9999 to the result"}
    ]
})


for message in result["messages"]:
    print(type(message).__name__, ":", message.content)
print(result["messages"][-1].content)