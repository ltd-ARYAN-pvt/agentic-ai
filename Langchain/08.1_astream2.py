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

async def background_work(start):
    # Simulate an independent I/O operation.
    await asyncio.sleep(0.5)

    return time.perf_counter() - start


async def main():
    start = time.perf_counter()

    # Start background work without waiting for it to finish.
    task = asyncio.create_task(background_work(start))

    print("LLM response:\n")

    async for chunk in chain.astream({
        "topic": "how TCP establishes a connection"
    }):
        print(chunk, end="", flush=True)

    print("\n\nLLM stream completed.")

    # Retrieve the result of the background task.
    background_elapsed = await task

    print(
        f"Background task completed after "
        f"{background_elapsed:.3f}s"
    )
    print(
        f"Total elapsed time: "
        f"{time.perf_counter() - start:.3f}s"
    )


asyncio.run(main())
