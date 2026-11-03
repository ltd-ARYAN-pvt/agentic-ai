import asyncio
import time
import statistics

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


def run_sync():
    start = time.perf_counter()

    results = [
        chain.invoke({"topic": topic})
        for topic in topics
    ]

    return time.perf_counter() - start, results


async def run_async():
    start = time.perf_counter()

    results = await asyncio.gather(
        *[
            chain.ainvoke({"topic": topic})
            for topic in topics
        ]
    )

    return time.perf_counter() - start, results


async def benchmark():
    # Warm up the model and connection first.
    await chain.ainvoke({"topic": "operating systems"})

    sync_times = []
    async_times = []

    for trial in range(5):
        # Alternate the order between trials.
        if trial % 2 == 0:
            sync_time, _ = run_sync()
            async_time, _ = await run_async()
        else:
            async_time, _ = await run_async()
            sync_time, _ = run_sync()

        sync_times.append(sync_time)
        async_times.append(async_time)

        print(
            f"Trial {trial + 1}: "
            f"sync={sync_time:.2f}s, "
            f"async={async_time:.2f}s"
        )

    sync_median = statistics.median(sync_times)
    async_median = statistics.median(async_times)

    print("\n--- Benchmark Summary ---")
    print(f"Sync median:  {sync_median:.2f}s")
    print(f"Async median: {async_median:.2f}s")

    improvement = (
        (sync_median - async_median) / sync_median
    ) * 100

    print(f"Async improvement: {improvement:.1f}%")


asyncio.run(benchmark())