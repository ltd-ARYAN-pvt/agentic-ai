from langchain_ollama import OllamaEmbeddings
from utils import getEmbeddedModel

# Initialize the embedding model
embeddings = OllamaEmbeddings(
    model=getEmbeddedModel()
)

text = "TCP provides reliable data delivery."

# Convert text into a vector
vector = embeddings.embed_query(text)

print("Vector:", vector)
print("Number of dimensions:", len(vector))