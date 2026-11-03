from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage
from utils import getmodel

llm=ChatOllama(
    model=getmodel(),
    temperature=0
)

message=[
    SystemMessage(
        # content="You are a precise computer science tutor."
        content="You are a strict interviewer; never give the full answer immediately."
    ),
    HumanMessage(
        content="What are the difference between asymptotic function and mathematical functions?"
    )
]

response=llm.invoke(message)

print("Content:", response.content)
print("Message ID:", response.id)
print("Response metadata:", response.response_metadata)
print("Usage:", response.usage_metadata)
print(type(response), type(response.content))