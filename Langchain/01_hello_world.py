from langchain_ollama import ChatOllama

#--> Initialize the local language model
llm = ChatOllama(
    model="llama3.2:3b",
    temperature=0.7,
    validate_model_on_init=True
)

#--> Send a prompt
response = llm.invoke(
    "Explain agentic-ai in short."
)

print("Response type: ", type(response).__name__)
print("Answer:\n", response.content)
print("Usage metadata: ", response.usage_metadata)
print("Response metadata: ",response.response_metadata)