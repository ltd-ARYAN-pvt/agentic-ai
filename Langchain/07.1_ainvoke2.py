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

topics = [
    "process scheduling",
    "virtual memory",
    "deadlocks",
]


#--> Async
async def main():
    start = time.perf_counter()

    results = await asyncio.gather(
        *[
            chain.ainvoke({"topic": topic})
            for topic in topics
        ]
    )

    elapsed = time.perf_counter() - start

    for topic, result in zip(topics, results):
        print(f"\n{'=' * 40}")
        print(f"TOPIC: {topic}")
        print(result)

    print(f"\nTotal elapsed time: {elapsed:.2f} seconds")


asyncio.run(main())

# #--> Sync
# start = time.perf_counter()
# results=[
#     chain.invoke({"topic":topic}) for topic in topics
# ]
# elapsed = time.perf_counter() - start
# for topic, result in zip(topics, results):
#     print(f"\n{'=' * 40}")
#     print(f"TOPIC: {topic}")
#     print(result)
# print(f"\nTotal elapsed time: {elapsed:.2f} seconds")