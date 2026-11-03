from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
from utils import getmodel

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a angry computer science tutor and don't like to explain {topic} again and again."),
    ("human", "Explain {topic} in {difficulty} terms.")
])

llm = ChatOllama(
    model=getmodel(),
    temperature=0,
)

messages = prompt.invoke({"topic": "recursion", "difficulty":"advanced"})
print(messages)

response = llm.invoke(messages)
print(response.content)