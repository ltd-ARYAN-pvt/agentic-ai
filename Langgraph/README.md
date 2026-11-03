# LangGraph Journey 🚀

A hands-on learning repository for understanding **LangGraph step by step**, from basic graphs to tool-using LLM agents.

This repository is built around small, numbered Python examples. Each file focuses on one concept so that you can run it, inspect the output, modify it, and understand how the pieces fit together.

> **Current focus:** Learning LangGraph with Python and a local Ollama model, then preparing to integrate MCP (Model Context Protocol).

---

## What is LangGraph?

LangGraph is a framework for building stateful, controllable workflows and agents with language models.

A useful way to think about the core pieces:

- **State** — the data shared throughout a graph run.
- **Nodes** — functions or components that perform work and return state updates.
- **Edges** — define what runs next.
- **Conditional edges** — choose the next node based on state or logic.
- **Checkpointers** — save graph state so workflows can persist or resume.
- **Tools** — functions a model can request an agent to execute.

LangGraph is especially useful when an application needs branching, loops, parallel work, memory, human approval, or tool execution—not just a single prompt sent to an LLM.

## Learning path

The numbered examples follow the journey from fundamentals to agentic workflows.

| File | Topic | What it demonstrates |
|---|---|---|
| `01_first_graph.py` | First graph | Build and invoke a basic graph with nodes and edges. |
| `02_basic_trace.py` | Basic tracing | Inspect the sequence of graph execution and understand what runs. |
| `03_conditional_edges.py` | Conditional routing | Choose a path based on state or a routing function. |
| `04_loops.py` | Loops | Route through a workflow repeatedly until a condition is met. |
| `05_parallel.py` | Parallel execution | Run independent graph branches in parallel. |
| `06_parallel_and_reducer.py` | Parallelism and reducers | Combine state updates from multiple branches with a reducer. |
| `07_checkpointer_demo.py` | Checkpointing | Save graph state using a checkpointer. |
| `08_short_term_memoey.py` | Short-term memory | Use thread-scoped checkpointed state for conversation continuity. |
| `09_long_term_memory.py` | Long-term memory | Store and retrieve information across different threads. |
| `10_hitl.py` | Human-in-the-loop (HITL) | Pause a workflow for human input or approval, then resume it. |
| `11_streaming.py` | Graph streaming | Observe graph progress as the workflow runs. |
| `12_llm_with_streaming.py` | LLM streaming | Explore streaming model output within an agent workflow. |
| `13_subgraph.py` | Subgraphs | Compose a reusable graph inside a larger graph. |
| `14_toolnode.py` | Tool-using agent | Connect a chat model to tools using `ToolNode` and `tools_condition`. |
| `15_toolnode_exception_handling.py` | Tool error handling | Explore how tool errors can be handled and returned to the model. |
| `16_retries_and_iteration_limit.md` | Retries and iteration limits | Learn tool-level retries, agent-level retries, error handling, and `recursion_limit`. |
| `17_reusable_tools_and_configurations.md` | Reusable tools and configuration | Organize tools, model settings, graph construction, and application entry points. |

The two `.md` files are lesson notes rather than executable Python scripts.

### The journey at a glance

```text
Graph basics
    ↓
Routing and loops
    ↓
Parallel branches and reducers
    ↓
Checkpointing and memory
    ↓
Human approval and streaming
    ↓
Subgraphs
    ↓
Tool-calling agents
    ↓
Errors, retries, and execution limits
    ↓
Reusable project structure
    ↓
Next: MCP integration
```

---

## Repository structure

```text
LangGraph/
├── .env
├── utils.py
├── 01_first_graph.py
├── 02_basic_trace.py
├── 03_conditional_edges.py
├── 04_loops.py
├── 05_parallel.py
├── 06_parallel_and_reducer.py
├── 07_checkpointer_demo.py
├── 08_short_term_memoey.py
├── 09_long_term_memory.py
├── 10_hitl.py
├── 11_streaming.py
├── 12_llm_with_streaming.py
├── 13_subgraph.py
├── 14_toolnode.py
├── 15_toolnode_exception_handling.py
├── 16_retries_and_iteration_limit.md
├── 17_reusable_tools_and_configurations.md
└── README.md
```

`utils.py` contains shared utilities used by the examples (for example, model selection/configuration, depending on its implementation). Check the file before running an example to see what it provides.

> **Naming note:** `08_short_term_memoey.py` uses the spelling present in the current repository. You can rename it to `08_short_term_memory.py` later if you want to correct the typo; remember to update any references.

---

## Prerequisites

- Python 3.10 or newer is a reasonable baseline; check the version required by your installed LangGraph/LangChain packages.
- Basic Python knowledge: functions, imports, type hints, dictionaries, and exceptions.
- Familiarity with LLMs and chat messages is helpful.
- [Ollama](https://ollama.com/) installed and running if an example uses a local Ollama model.
- Git is optional but useful for tracking changes.

## Environment setup

### 1. Create and activate a virtual environment

**Windows PowerShell**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**macOS / Linux**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install the packages used by the examples

The exact dependencies depend on the imports in your files. A starting point for this journey may be:

```bash
pip install -U langgraph langchain-core langchain-ollama python-dotenv tenacity
```

Install any additional packages imported by a particular example. If you later add a `requirements.txt`, use that as the reproducible installation source.

### 3. Prepare Ollama

If you're using the model from the tool-calling examples, make sure Ollama is installed and the model is available:

```bash
ollama pull llama3.2:3b
ollama list
```

Ensure the Ollama service is running before invoking a script that calls the model.

### 4. Configure environment variables safely

Some examples may use `.env` or `utils.py`. Review the code to learn which variables are required.

- Keep real API keys and secrets in your local `.env`.
- **Never commit `.env` to a public repository.**
- Add `.env` and virtual-environment directories to `.gitignore`.
- If sharing the repository, provide a `.env.example` containing placeholder values only, not real secrets.

Example `.gitignore`:

```gitignore
.env
.venv/
venv/
__pycache__/
*.py[cod]
```

Example `.env.example` (adapt the names to what your code actually reads):

```dotenv
# Add the environment variable names required by your project.
# Use placeholders only; never put real credentials here.
```

---

## Running the examples

Run one script at a time from the repository directory. For example:

```powershell
python .\01_first_graph.py
python .\03_conditional_edges.py
python .\14_toolnode.py
python .\15_toolnode_exception_handling.py
```

On macOS/Linux, the equivalent is:

```bash
python 01_first_graph.py
```

For the lesson notes, open the Markdown files in your editor:

- `16_retries_and_iteration_limit.md`
- `17_reusable_tools_and_configurations.md`

### Suggested study routine

For each example:

1. Read the complete script before running it.
2. Identify the state schema, nodes, and edges.
3. Predict what should happen.
4. Run the script and compare the output with your prediction.
5. Change one thing—an input, condition, edge, reducer, or prompt—and run it again.
6. Write down what changed and why.

This approach helps you understand the behavior instead of only copying code.

---

## Core concepts covered

### State and updates

A node usually returns a **partial state update**. Keys not included in that update remain unchanged, while returned keys update the graph state. Reducers determine how concurrent updates to a key are combined.

### Conditional edges and loops

A routing function can choose the next node. Loops are useful for retrying work or evaluating output, but they need clear exit conditions.

### Parallel execution and reducers

Independent branches can run in parallel. When multiple branches update the same state key, a reducer such as `operator.add` can define how their values are combined. List concatenation does not automatically remove duplicates.

### Checkpointing and memory

- **Short-term memory** commonly uses checkpointed state associated with a conversation/thread.
- **Long-term memory** can store information that should be available across different threads.
- A checkpointer or store does not automatically make an LLM remember something; the graph must read and use the stored data.
- In-memory implementations are useful for learning but do not persist after the process exits.

### Human-in-the-loop

LangGraph can pause execution for human input or approval and resume later. Use a checkpointer and the same thread identifier when resuming a paused execution. For sensitive actions, validate the proposed operation and require approval where appropriate.

### Streaming

Graph streaming can expose intermediate state updates or values. Model-token streaming is distinct from receiving graph updates: a node that uses a normal blocking model invocation generally waits for the model response to finish.

### Tool-calling agents

A common pattern is:

1. The assistant receives messages and may request a tool.
2. `tools_condition` routes to `ToolNode` if the assistant message contains structured tool calls.
3. `ToolNode` executes the requested tools.
4. Tool results return to the assistant.
5. The assistant either requests another tool or produces a final response.

For Ollama, tool-calling behavior can depend on the model and installed package versions. If the model prints JSON-like text instead of producing structured `tool_calls`, the graph may not route to `ToolNode`. Inspect `response.tool_calls` while debugging.

---

## Troubleshooting notes

### The model prints JSON instead of calling a tool

Inspect the assistant message:

```python
response = llm.invoke(messages)

print("Content:", repr(response.content))
print("Tool calls:", response.tool_calls)
print("Invalid tool calls:", response.invalid_tool_calls)
```

A genuine structured tool call should appear in `response.tool_calls`. JSON-looking text in `response.content` is just text. A clear system prompt can help a compatible model follow the intended tool-calling behavior, but cannot guarantee support.

### The graph keeps looping

- Inspect your edges and conditional routing.
- Make sure the assistant can reach `END` when no tool call is requested.
- Add explicit counters or stopping conditions where needed.
- Use `recursion_limit` as a safeguard and handle `GraphRecursionError`.

### A tool error stops execution

Decide whether the tool should return a normal error result, raise an exception, or retry a transient failure. `ToolNode(handle_tool_errors=True)` can handle exceptions, but it does not automatically implement a retry policy.

### Imports fail

- Run scripts from the repository root.
- Make sure the virtual environment is activated.
- Check the installed packages and import names.
- Confirm that `utils.py` and any local modules are in the expected location.

---

## What comes next: MCP

The next phase of this journey is **Model Context Protocol (MCP)**.

Planned topics:

1. Why MCP exists and how it relates to LangChain and LangGraph.
2. MCP architecture: host, client, and server.
3. Tools, resources, and prompts.
4. Building a Python MCP server.
5. Connecting an MCP client to the existing LangGraph/Ollama agent.
6. Transport options and security considerations.
7. A small end-to-end project.

**The key distinction:** LangGraph orchestrates your agent's workflow. MCP standardizes how applications discover and interact with tools and other context exposed by MCP servers. They can be used together.

---

## Contributing or sharing this journey

This repository is a learning log, so examples may be intentionally small or simplified. When sharing it:

- Explain any local configuration requirements.
- Never include `.env`, API keys, or other credentials.
- Add a `requirements.txt` once dependencies are settled.
- Mention any model-specific assumptions.
- Keep examples small enough that each one teaches a clear concept.

## License

No license is specified in this repository yet. If you intend to publish or invite others to reuse the code, choose and add an appropriate license.
