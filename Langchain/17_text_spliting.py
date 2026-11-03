from langchain_text_splitters import RecursiveCharacterTextSplitter
from pathlib import Path
from langchain_core.documents import Document

file_path = Path("computer_networks.txt")
doc = Document(
    page_content=file_path.read_text(encoding="utf-8"),
    metadata={"source": str(file_path)}
)

splitter = RecursiveCharacterTextSplitter(
    chunk_size=150,
    chunk_overlap=30,
    separators=[" "]
)

chunks = splitter.split_documents([doc])

for i, chunk in enumerate(chunks):
    print(f"\n--- Chunk {i + 1} ---")
    print(chunk.page_content)
    print("Metadata:", chunk.metadata)
    print("Characters:", len(chunk.page_content))