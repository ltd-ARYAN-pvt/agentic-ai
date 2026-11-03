from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_ollama import ChatOllama
from utils import getmodel

prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are a technically accurate computer science tutor."
    ),
    (
        "human",
        "Explain {topic} at a {difficulty} level."
    ),
])

llm = ChatOllama(
    model=getmodel(),
    temperature=0,
)

chain = prompt | llm | StrOutputParser()

topic = input("Enter a CS topic: ")
difficulty = input("Enter difficulty: ")

print("\nTutor:\n")

for chunk in chain.stream({
    "topic": topic,
    "difficulty": difficulty,
}):
    print(chunk, end="", flush=True)

print("\n")