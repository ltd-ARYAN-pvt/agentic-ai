from langchain_ollama import OllamaEmbeddings

embeddings = OllamaEmbeddings(
    model="nomic-embed-text"
)

chunks = [
    "TCP provides reliable data delivery.",
    "UDP is connectionless and has lower overhead.",
    "DNS translates domain names into IP addresses."
]

vectors = embeddings.embed_documents(chunks)

print("Number of chunks:", len(chunks))
print("Number of vectors:", len(vectors))
print("Dimensions per vector:", len(vectors[0]))

'''
embed_documents(texts) ->	Creates vectors for your document chunks during indexing.
embed_query(text) ->	Creates a vector for the user's question during retrieval.
'''