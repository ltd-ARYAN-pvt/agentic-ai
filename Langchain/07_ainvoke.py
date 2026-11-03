import asyncio
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_ollama import ChatOllama
from utils import getmodel
import time

prompt = ChatPromptTemplate.from_template(
    "Explain {topic} in approximately 100 words."
)

llm = ChatOllama(model=getmodel(), temperature=0)

chain = prompt | llm | StrOutputParser()


async def main():
    start = time.perf_counter()
    response = await chain.ainvoke({
        "topic": "process scheduling in operating systems"
    })
    elapsed = time.perf_counter() - start

    print(response)
    print(f"\nTotal elapsed time: {elapsed:.3f} seconds")

asyncio.run(main())