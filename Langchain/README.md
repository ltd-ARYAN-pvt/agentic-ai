# 🦜 LangChain Learning Lab

### From your first LLM call to a local RAG pipeline — one step at a time.

**A hands-on LangChain journey using Python, Ollama, and ChromaDB**

![Python](https://img.shields.io/badge/Python-3.x-3776AB?logo=python&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-LCEL-1C3C3C)
![Ollama](https://img.shields.io/badge/LLM-Ollama-black)
![RAG](https://img.shields.io/badge/Project-RAG-7C3AED)

[🚀 Setup](#-quick-start) · [🗺️ Learning roadmap](#-learning-roadmap) ·
[📚 Script guide](#-script-by-script-guide) · [🧠 RAG
flow](#-the-rag-pipeline) · [🛠️ Troubleshooting](#️-troubleshooting)
---

## 👋 Welcome!

This repository is my practical notebook for learning **LangChain**,
starting with basic model calls and progressing to tool calling, agents,
and Retrieval-Augmented Generation (RAG).

The goal isn't just to run scripts. It's to understand **what each
component does, why it exists, and how data moves through a chain**.

> **Tip:** Learn by doing: run one script, inspect its output, change
> one thing, and run it again. Small experiments make the concepts
> stick.

## 🎯 What you'll learn

-   [x] Call a local language model using LangChain and Ollama
-   [x] Build reusable prompts and LCEL chains
-   [x] Parse model output into useful formats
-   [x] Stream responses and use asynchronous calls
-   [x] Request structured output
-   [x] Define tools and understand the tool-calling cycle
-   [x] Build simple agents
-   [x] Load documents, split text, and create embeddings
-   [x] Store and retrieve document chunks with Chroma
-   [x] Build a basic RAG chain
-   [ ] Improve RAG quality by inspecting retrieved context and
    evaluating answers

*The final item is a suggested next step, not a claim that a script
already exists.*

---

## 🚀 Quick start

### 1. Prerequisites

Install these before running the examples:

-   **Python** (use a version supported by your installed LangChain
    packages)
-   **Ollama** — runs the model locally
-   The chat model `llama3.2:3b`
-   The embedding model `nomic-embed-text`

Pull the models in PowerShell:

```powershell
ollama pull llama3.2:3b
ollama pull nomic-embed-text
```

Check that Ollama can see them:

```powershell
ollama list
```

Make sure the Ollama service is running before executing scripts.
Depending on your installation, Ollama may already run in the
background.

### 2. Open the project folder

In PowerShell, navigate to the folder where this repository lives. For
example:

```powershell
cd "C:\path\to\your\Langchain"
```

Replace the example path with your actual project path.

### 3. Activate the virtual environment

This repository includes a `venv` folder. Activate it in PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

If PowerShell blocks activation because of its execution policy, you can
run scripts with the current user policy adjusted only if you understand
and are allowed to change that setting. Alternatively, run the
interpreter directly:

```powershell
.\venv\Scripts\python.exe .\01_hello_world.py
```

### 4. Install dependencies if needed

If the environment already works, you don't need to reinstall
everything. If imports fail, install the packages used by the examples:

```powershell
python -m pip install -U langchain-core langchain-ollama langchain-chroma langchain-community langchain-text-splitters chromadb pydantic python-dotenv
```

Some scripts may use additional integrations depending on their
contents. Install the package required by the specific missing import
rather than installing every possible LangChain integration.

### 5. Configure environment variables

The repository contains a `.env` file. Keep secrets out of Git and never
paste API keys into a public README.

If your scripts use `python-dotenv`, load the file like this:

```python
from dotenv import load_dotenv

load_dotenv()
```

**Note:** The examples use local Ollama models, so a hosted-model API
key is not normally required for the core workflow. Check `utils.py` and
individual scripts to confirm the exact configuration.

### 6. Run your first example

```powershell
python .\01_hello_world.py
```

Then continue in order using the guide below.

---

## 🗺️ Learning roadmap

### Stage 1 — Chat models and messages
(01–02)
**Goal:** Understand the basic request/response loop.

-   `01_hello_world.py` — first model interaction
-   `02_systemand human_messages.py` — system and human messages

**Key idea:** A chat model takes messages as input and returns an AI
message. The result is often an `AIMessage`, and its text is available
through `.content`.

Try it:
1. Change the question.
2. Compare a system instruction with a human message.
3. Inspect the returned object and then print only `.content`.

### Stage 2 — Prompt templates and LCEL
(03–05)
**Goal:** Turn prompts into reusable pipelines.

-   `03_prompt_templates.py` — parameterized prompt templates
-   `04_langchain_expression_language.py` — compose components with
    `|`
-   `05_cs_tutor_with_output_parser.py` — build a focused tutor and
    parse the response

**Key idea:** LCEL (LangChain Expression Language) lets you compose
runnable components into a chain.

```python
chain = prompt | llm | parser
result = chain.invoke({"topic": "TCP"})
```

The exact input keys depend on the prompt template.

### Stage 3 — Experiments, streaming, and async
(06–08)
**Goal:** Explore different ways to execute a chain.

-   `06.1_exp.py` — experiment script; inspect its code for the
    specific concept tested
-   `06_streaming.py` — stream output as it arrives
-   `07_ainvoke.py` and `07.1_ainvoke2.py` — asynchronous invocation
    examples
-   `07.2_stats.py` — statistics/measurements experiment
-   `08_astream.py` and `08.1_astream2.py` — asynchronous streaming
    examples

**Key ideas:**

-   `.invoke()` runs a chain for one input and returns the completed
    result.
-   `.stream()` yields output incrementally.
-   `.ainvoke()` is the asynchronous version of `.invoke()`.
-   `.astream()` yields asynchronous output chunks.
-   A streamed chunk is not guaranteed to equal exactly one model token.

### Stage 4 — Structured output (09)
**Goal:** Get data in a predictable shape rather than free-form prose.

-   `09_structured_output.py`
-   `09_structured_op2.py`

Structured output can use a schema, such as a Pydantic model, to
describe expected fields and types. Always validate the returned data; a
schema or instruction does not guarantee that every model will comply
perfectly.

### Stage 5 — Tools and agents (10–15)
**Goal:** Let a model choose and request external functions.

  Script                        Focus
  ----------------------------- --------------------------------------
  `10_tools.py`                 Define a tool
  `11_tools_with_llm.py`        Expose tools to a model
  `12_complete_tool_cycle.py`   Understand the tool-call round trip
  `13_tool_calling_loop.py`     Handle repeated tool calls
  `14_agents.py`                Agent example
  `15_react_agent.py`           ReAct-style reasoning/action pattern

**Important distinction:** Binding tools to a model tells it which tools
are available. It does **not**, by itself, execute those tools. A
tool-calling workflow must execute the requested function, return its
result to the model, and continue when necessary.

Small local models may produce invalid tool names or arguments. Inspect
tool calls and validate inputs before executing side effects.

### Stage 6 — Documents and chunking
(16–17)
**Goal:** Prepare source material for retrieval.

-   `16_Document_loadin.py` — document loading
-   `17.1_exp.py` — chunking experiment
-   `17_text_spliting.py` — text splitting

A LangChain `Document` commonly contains:

```python
Document(
    page_content="The text of this chunk...",
    metadata={"source": "computer_networks.txt"}
)
```

Chunking breaks long documents into smaller pieces that can be embedded
and retrieved. `chunk_size` is a target size, and `chunk_overlap`
repeats some content between adjacent chunks to reduce the chance of
losing context at boundaries.

### Stage 7 — Embeddings and vector stores
(18–19)
**Goal:** Search text by semantic similarity.

-   `18.0_embedded_model.py` — embedding model
-   `18.1_embedded_model_2.py` — embedding experiment
-   `19_vector_store.py` — store and search vectors

The project uses the local embedding model `nomic-embed-text` and
ChromaDB. Embeddings represent text as numeric vectors; a vector store
indexes those vectors so related chunks can be retrieved for a query.

### Stage 8 — RAG chain (20)
**Goal:** Ground a model's answer in retrieved documents.

-   `20_rag_chain.py` — connect retrieval, prompt construction, model
    generation, and output parsing
-   `computer_networks.txt` — sample source document
-   `chroma_db/` — persisted Chroma data

The example uses `llama3.2:3b` for generation and `nomic-embed-text` for
embeddings.

---

## 📚 Script-by-script guide

Use this as a navigation index. Some filenames are experiments, so their
exact behavior should be confirmed by opening the corresponding script.

     \# File                                    Topic
  ----- --------------------------------------- -----------------------------------------
     01 `01_hello_world.py`                     First model call
     02 `02_systemand human_messages.py`        Message roles
     03 `03_prompt_templates.py`                Prompt templates
     04 `04_langchain_expression_language.py`   LCEL and pipes
     05 `05_cs_tutor_with_output_parser.py`     Output parsing
     06 `06_streaming.py`                       Streaming
     07 `07_ainvoke.py`                         Async invocation
     08 `07.1_ainvoke2.py`                      Async experiment
     09 `07.2_stats.py`                         Stats experiment
     10 `08_astream.py`                         Async streaming
     11 `08.1_astream2.py`                      Async streaming experiment
     12 `09_structured_output.py`               Structured output
     13 `09_structured_op2.py`                  Structured output experiment
     14 `10_tools.py`                           Tool definition
     15 `11_tools_with_llm.py`                  Model + tools
     16 `12_complete_tool_cycle.py`             Tool execution cycle
     17 `13_tool_calling_loop.py`               Repeated tool calls
     18 `14_agents.py`                          Agent example
     19 `15_react_agent.py`                     ReAct-style agent
     20 `16_Document_loadin.py`                 Document loading
     21 `17.1_exp.py`                           Text-splitting experiment
     22 `17_text_spliting.py`                   Text splitting
     23 `18.0_embedded_model.py`                Embeddings
     24 `18.1_embedded_model_2.py`              Embedding experiment
     25 `19_vector_store.py`                    Chroma vector store
     26 `20_rag_chain.py`                       End-to-end RAG
    — `utils.py`                              Shared helper(s), including model setup
    — `computer_networks.txt`                 Sample knowledge source
    — `chroma_db/`                            Persisted vector database
    — `venv/`                                 Local Python environment

**Naming note:** A few filenames contain spaces, dots, or inconsistent
spelling. They can still run, but consistent names such as
`02_system_and_human_messages.py` and `17_text_splitting.py` are easier
to maintain. Rename carefully and update any references.

---

## 🧩 Core concepts, explained simply

### What is a Runnable?
A **Runnable** is a LangChain component that follows a common execution
interface, typically including methods such as `.invoke()`, `.stream()`,
and asynchronous equivalents.

This common interface makes it possible to connect components with
LCEL's `|` operator.

```python
from langchain_core.runnables import RunnableLambda

chain = (
    RunnableLambda(lambda x: x * 2)
    | RunnableLambda(lambda x: x + 10)
)

print(chain.invoke(5))  # 20
```

Read the pipeline from left to right: `5 → 10 → 20`.

### Why does `|` work?
The pipe operator composes compatible Runnables. The output of the
component on the left becomes the input of the component on the right.
Composition defines the pipeline; calling `.invoke()` runs it.

```python
chain = prompt | llm | StrOutputParser()
answer = chain.invoke({"question": "How does TCP work?"})
```

The data passed to `invoke()` must match what the first component
expects.

### What does `RunnablePassthrough()` do?
It passes the input through unchanged. In a RAG chain, this is useful
when the original question must be preserved while another branch
retrieves context.

```python
"question": RunnablePassthrough()
```

### What does a dictionary of Runnables
mean?
In LCEL, a mapping like this is automatically treated as parallel
branches:

```python
{
    "context": retriever | format_docs,
    "question": RunnablePassthrough(),
}
```

Both branches receive the same original input. Their outputs are
collected into a dictionary:

```python
{
    "context": "Relevant retrieved text...",
    "question": "How does TCP ensure reliable delivery?"
}
```

That dictionary can then be passed to a prompt expecting `{context}` and
`{question}`.

### What is the difference between an embedding and a
vector store?
-   **Embedding model:** converts text into a vector (a list of
    numbers).
-   **Vector store:** stores vectors and associated text/metadata, then
    retrieves likely relevant items for a query.
-   **Retriever:** gives a chain a convenient way to search the vector
    store for relevant documents.

Similarity is a ranking signal, not a guarantee that a chunk contains
the answer.

---

## 🧠 The RAG pipeline

RAG means **Retrieval-Augmented Generation**. Instead of asking the
model to answer from its parameters alone, the application retrieves
relevant material and supplies it as context.

``` mermaid
flowchart TD
    A[Source documents] --> B[Load documents]
    B --> C[Split into chunks]
    C --> D[Create embeddings]
    D --> E[(Chroma vector store)]
    Q[User question] --> QE[Embed/search query]
    E --> R[Retrieve relevant chunks]
    QE --> R
    R --> F[Format context]
    Q --> P[Build prompt]
    F --> P
    P --> L[Ollama chat model]
    L --> O[Parse output]
    O --> Z[Answer]
```

### The RAG chain in this project

The core flow in `20_rag_chain.py` is conceptually:

```python
rag_chain = (
    {
        "context": retriever | format_docs,
        "question": RunnablePassthrough(),
    }
    | prompt
    | llm
    | StrOutputParser()
)

answer = rag_chain.invoke("How does TCP ensure reliable delivery?")
print(answer)
```

### What happens when `.invoke(question)` runs?

1.  The question enters the mapping at the start of the chain.
2.  The `context` branch sends it to the retriever and formats the
    returned documents.
3.  The `question` branch passes the original question through
    unchanged.
4.  The branches produce a dictionary containing `context` and
    `question`.
5.  The prompt fills in those two variables.
6.  The LLM generates an answer from the prompt.
7.  `StrOutputParser()` converts the model message to a plain string.

> \[!IMPORTANT\] The prompt can ask the model to use only the supplied
> context, but this instruction is not a mathematical guarantee. Inspect
> retrieved chunks and verify answers when accuracy matters.

### RAG debugging checklist

When an answer is poor, debug in this order:

-   [ ] Does the source file contain the answer?
-   [ ] Did the loader read the right file?
-   [ ] Are chunk boundaries preserving the relevant information?
-   [ ] Does the retriever return the expected chunks?
-   [ ] Is `k` (the number of retrieved chunks) appropriate?
-   [ ] Does the formatted context contain useful text and source
    metadata?
-   [ ] Does the prompt clearly tell the model how to use context?
-   [ ] Does the model answer faithfully, or invent unsupported details?

A useful next improvement is to print retrieved documents before
invoking the complete RAG chain:

```python
question = "How does TCP ensure reliable delivery?"
docs = retriever.invoke(question)

for i, doc in enumerate(docs, start=1):
    print(f"\n--- Retrieved chunk {i} ---")
    print(doc.page_content)
    print("Metadata:", doc.metadata)
```

This helps separate **retrieval problems** from **generation problems**.

---

## 🗂️ Project structure

``` text
Langchain/
├── .env
├── utils.py
├── computer_networks.txt
├── 01_hello_world.py
├── ...
├── 19_vector_store.py
├── 20_rag_chain.py
├── chroma_db/
├── venv/
└── README.md
```

-   `utils.py` — shared helper functions; inspect it to see the model
    configuration.
-   `.env` — local environment configuration. Do not commit secrets.
-   `computer_networks.txt` — source content for the RAG example.
-   `chroma_db/` — persisted vector-store files. Rebuild this if the
    source documents or embedding setup changes.
-   `venv/` — local virtual environment; it is usually not necessary
    to commit it to Git.

This is a simplified overview; the full folder also contains the
experiment scripts listed above.

---

## 🛠️ Troubleshooting

### PowerShell says the script cannot be
run
Try the Python executable inside the environment directly:

```powershell
.\venv\Scripts\python.exe .\01_hello_world.py
```

This avoids activating the environment. If the issue is an
execution-policy restriction, follow your organization's device policy
rather than changing security settings blindly.

### Python says `ModuleNotFoundError`
Confirm which interpreter is running:

```powershell
python --version
python -m pip --version
```

Then install the package that provides the missing module into that same
environment. For example:

```powershell
python -m pip install langchain-ollama langchain-chroma langchain-core
```

### Ollama cannot find the model
Check installed models:

```powershell
ollama list
```

Pull the model if it is missing:

```powershell
ollama pull llama3.2:3b
ollama pull nomic-embed-text
```

Use the exact model name configured in the Python script.

### Chroma returns no useful documents
Check that:

-   The vector store was created from the expected documents.
-   The collection name and persistence directory match between creation
    and reopening.
-   The embedding model used for retrieval matches the one used to index
    the documents.
-   The question uses terms or concepts present in the source material.
-   The correct collection is being queried.

If you change source data or embedding models, consider rebuilding the
local vector store rather than mixing incompatible embeddings.

### The answer ignores the retrieved
context
Print the retrieved chunks, inspect the final prompt, and try a smaller,
more focused question. A small local model can misunderstand
instructions or produce unsupported claims even when the retrieval step
succeeds.

---

## 🔐 Good habits

-   Keep `.env` private; add it to `.gitignore` if it contains secrets.

-   Usually exclude `venv/`, `__pycache__/`, and generated cache files
    from version control.

-   Decide intentionally whether to track `chroma_db/`. It can be
    regenerated, and its files may be large.

-   Record package versions in a `requirements.txt` when the environment
    is stable:

    ```powershell
    python -m pip freeze > requirements.txt
    ```

-   Validate model output and tool arguments before relying on them.

-   Treat retrieved documents as data, not as trusted instructions.

-   Inspect intermediate outputs before assuming a complete chain is
    correct.

A possible `.gitignore`:

``` gitignore
venv/
__pycache__/
*.py[cod]
.env
chroma_db/
```

Only ignore `chroma_db/` if you are comfortable regenerating the vector
store when needed.

---

## ✅ Learning checklist

Use this checklist as you revise. Tick items off in your own copy of the
README.

-   [ ] I can explain the difference between a chat model and a prompt
    template.
-   [ ] I can build a chain with `prompt | llm | parser`.
-   [ ] I understand `.invoke()`, `.stream()`, `.ainvoke()`, and
    `.astream()`.
-   [ ] I know the difference between defining a tool and executing a
    tool call.
-   [ ] I can explain how an agent uses tools.
-   [ ] I can load a document and split it into chunks.
-   [ ] I understand what embeddings represent.
-   [ ] I can create and reopen a Chroma vector store.
-   [ ] I can inspect which chunks a retriever returns.
-   [ ] I can explain every step in `20_rag_chain.py`.
-   [ ] I can debug whether a bad RAG answer came from retrieval, prompt
    construction, or generation.

---

## 🚧 Suggested next steps

1.  **Make RAG observable:** print retrieved chunks, metadata, and the
    final context.
2.  **Experiment with retrieval:** compare `k=2` with `k=4` and observe
    which chunks change.
3.  **Evaluate answers:** prepare a small set of questions with expected
    evidence and check whether the answer is supported by the retrieved
    text.
4.  **Add source-aware answers:** preserve document metadata so you can
    show where an answer came from.
5.  **Keep the next topic separate:** once the basics are comfortable,
    study LangGraph for stateful workflows and LangSmith for tracing and
    evaluation.

---

{align="center"}
### 🌱 Build, inspect, experiment, repeat.

**The real goal is not memorizing APIs — it's understanding the flow
of data through an AI application.**
