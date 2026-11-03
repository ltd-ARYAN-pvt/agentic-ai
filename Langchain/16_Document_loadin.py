from pathlib import Path
from langchain_core.documents import Document

# Create a sample text file
text = """
TCP (Transmission Control Protocol) is a connection-oriented
transport layer protocol. It provides reliable data delivery,
sequencing, acknowledgements, and retransmission.

UDP (User Datagram Protocol) is a connectionless transport
layer protocol. It has lower overhead and does not guarantee
delivery, sequencing, or retransmission.

TCP is commonly used for reliable transfers, while UDP is
often useful for real-time applications such as online gaming,
voice calls, and live streaming.
"""

file_path = Path("computer_networks.txt")
file_path.write_text(text.strip(), encoding="utf-8")

# Load the file and represent it as a LangChain Document
doc = Document(
    page_content=file_path.read_text(encoding="utf-8"),
    metadata={"source": str(file_path)}
)

print("Document metadata:", doc.metadata)
print("Document characters:", len(doc.page_content))
print("\nDocument content:\n", doc.page_content)