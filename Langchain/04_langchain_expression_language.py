#--> LCEL

from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
from utils import getmodel

prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are a lazy but technically accurate computer science tutor."
    ),
    (
        "human",
        "Explain {topic} at an {difficulty} level."
    ),
])

llm = ChatOllama(
    model=getmodel(),
    temperature=0,
)

# Compose the components
chain = prompt | llm

# Execute the complete pipeline
response = chain.invoke({
    "topic": "recursion",
    "difficulty": "easy",
})

print(response.content)