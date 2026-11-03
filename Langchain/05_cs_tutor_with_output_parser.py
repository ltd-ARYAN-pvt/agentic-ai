
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_ollama import ChatOllama
from utils import getmodel

prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are a technically accurate computer science tutor. "
        "Explain concepts clearly and use examples when useful."
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

while True:
    topic = input("\nEnter a CS topic (or 'exit'): ").strip()

    if topic.lower() == "exit":
        break

    difficulty = input("Difficulty (beginner/intermediate/advanced): ").strip()

    try:
        answer = chain.invoke({
            "topic": topic,
            "difficulty": difficulty,
        })
        print("\nTutor:\n", answer)

    except Exception as exc:
        print(f"Error: {exc}")
