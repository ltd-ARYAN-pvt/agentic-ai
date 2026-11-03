from langchain_core.documents import Document
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma

# 1. Create documents
docs = [
    Document(
        page_content="TCP provides reliable data delivery using acknowledgements and retransmissions.",
        metadata={"topic": "TCP", "source": "networking.txt"}
    ),
    Document(
        page_content="UDP is connectionless and has lower overhead. It is useful for real-time applications.",
        metadata={"topic": "UDP", "source": "networking.txt"}
    ),
    Document(
        page_content="DNS translates domain names into IP addresses.",
        metadata={"topic": "DNS", "source": "networking.txt"}
    ),
]

# 2. Initialize the embedding model
embeddings = OllamaEmbeddings(
    model="nomic-embed-text"
)

# 3. Create the vector store and embed the documents
vector_store = Chroma.from_documents(
    documents=docs,
    embedding=embeddings,
    collection_name="networking_notes",
    persist_directory="./chroma_db",
)

print("Documents embedded and stored!")

# 4. Search by meaning
query = "Which protocol guarantees reliable delivery?"

results = vector_store.similarity_search(
    query=query,
    k=2,
)

# 5. Display retrieved documents
for i, doc in enumerate(results, 1):
    print(f"\nResult {i}")
    print("Text:", doc.page_content)
    print("Metadata:", doc.metadata)