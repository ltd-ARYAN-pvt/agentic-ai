import time
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_ollama import ChatOllama
from utils import getmodel

prompt = ChatPromptTemplate.from_template(
    "Explain how an operating system schedules processes "
    "in approximately 150 words."
)

llm = ChatOllama(model=getmodel(), temperature=0)

chain = prompt | llm | StrOutputParser()

start = time.perf_counter()
previous = start
first = True
chunk_count = 0
character_count = 0

for chunk in chain.stream({}):
    now = time.perf_counter()
    chunk_count += 1
    character_count += len(chunk)

    if first:
        print(f"Time to first chunk: {now - start:.3f}s")
        first = False
    else:
        print(
            f"Chunk {chunk_count}: "
            f"{len(chunk)} chars, "
            f"gap={now - previous:.3f}s"
        )

    print(chunk, end="", flush=True)
    previous = now

total = time.perf_counter() - start

print(f"\n\nChunks: {chunk_count}")
print(f"Characters: {character_count}")
print(f"Total time: {total:.3f}s")