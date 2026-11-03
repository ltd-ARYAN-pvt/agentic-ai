from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

text = (
    "TCP is reliable and connection-oriented. "
    "UDP is connectionless and has lower overhead. "
    "TCP uses acknowledgements and retransmissions. "
    "UDP does not guarantee delivery or ordering. "
    "TCP is useful for reliable transfers. "
    "UDP is useful for real-time applications."
)

doc = Document(page_content=text)

splitter = RecursiveCharacterTextSplitter(
    chunk_size=80,
    chunk_overlap=20,
    separators=[" "],
)

chunks = splitter.split_documents([doc])

for i, chunk in enumerate(chunks):
    print(f"\nChunk {i + 1}: {chunk.page_content}")