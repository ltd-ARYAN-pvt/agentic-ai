import asyncio
import time

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_ollama import ChatOllama
from utils import getmodel

prompt = ChatPromptTemplate.from_template(
    "Explain {topic} in approximately 100 words."
)

llm = ChatOllama(model=getmodel(), temperature=0)
chain = prompt | llm | StrOutputParser()

async def main():
    start = time.perf_counter()
    first_text_time = None
    chunks = 0

    async for chunk in chain.astream({
        "topic": "how TCP establishes a connection"
    }):
        now = time.perf_counter()

        if chunk:
            chunks += 1

            if first_text_time is None:
                first_text_time = now - start

        print(chunk, end="", flush=True)

    elapsed = time.perf_counter() - start

    print("\n\n--- Streaming Metrics ---")
    print(f"Time to first text: {first_text_time:.3f}s")
    print(f"Non-empty chunks: {chunks}")
    print(f"Total time: {elapsed:.3f}s")

asyncio.run(main())