from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

# 1. Load the existing vector store
embeddings = OllamaEmbeddings(model="nomic-embed-text")

vector_store = Chroma(
    collection_name="networking_notes",
    embedding_function=embeddings,
    persist_directory="./chroma_db",
)

# 2. Create the retriever
retriever = vector_store.as_retriever(
    search_kwargs={"k": 2}
)

# 3. Initialize the LLM
llm = ChatOllama(
    model="llama3.2:3b",
    temperature=0,
)

# 4. Create the prompt
prompt = ChatPromptTemplate.from_template("""
Answer the question using only the context below.
If the context does not contain the answer, say you don't
have enough information to answer.

Context:
{context}

Question:
{question}

Answer:
""")

# 5. Format retrieved documents into context text
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

# 6. Connect the components using LCEL
rag_chain = (
    {
        "context": retriever | format_docs,
        "question": RunnablePassthrough(),
    }
    | prompt
    | llm
    | StrOutputParser()
)

# 7. Ask a question
question = "How does TCP ensure reliable delivery?"

answer = rag_chain.invoke(question)

print("\nQuestion:", question)
print("\nAnswer:", answer)