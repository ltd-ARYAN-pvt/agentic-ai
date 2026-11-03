# LangGraph Core Concepts — A Practical Learning Guide 🚀

> A concept-first guide based on our LangGraph learning journey. It connects the ideas to the examples, questions, bugs, and fixes we discussed—not just API definitions.

## Table of Contents

1. [What Is LangGraph?](#1-what-is-langgraph)
2. [LangChain vs LangGraph](#2-langchain-vs-langgraph)
3. [The Four Building Blocks](#3-the-four-building-blocks)
4. [State Schemas: `TypedDict` and Pydantic](#4-state-schemas-typeddict-and-pydantic)
5. [Building and Compiling a Graph](#5-building-and-compiling-a-graph)
6. [Nodes Return Partial State Updates](#6-nodes-return-partial-state-updates)
7. [Normal Edges and Conditional Edges](#7-normal-edges-and-conditional-edges)
8. [Loops, Retries, and Iteration Limits](#8-loops-retries-and-iteration-limits)
9. [Reducers and Parallel Execution](#9-reducers-and-parallel-execution)
10. [Checkpointing and Short-Term Memory](#10-checkpointing-and-short-term-memory)
11. [Long-Term Memory with a Store](#11-long-term-memory-with-a-store)
12. [Human-in-the-Loop](#12-human-in-the-loop)
13. [Streaming](#13-streaming)
14. [Subgraphs](#14-subgraphs)
15. [LLM Tool Calling and `ToolNode`](#15-llm-tool-calling-and-toolnode)
16. [Tool Errors and Reliable Agent Behavior](#16-tool-errors-and-reliable-agent-behavior)
17. [Reusable Tools and Configuration](#17-reusable-tools-and-configuration)
18. [Common Confusions We Resolved](#18-common-confusions-we-resolved)
19. [A Mental Model to Keep](#19-a-mental-model-to-keep)
20. [Practice Questions](#20-practice-questions)

---

## 1. What Is LangGraph?

LangGraph is a framework for defining and running stateful workflows, especially workflows that involve LLMs, tools, branching, loops, memory, and human decisions.

Think of an agent as a process that may need to do more than answer once:

1. Receive a request.
2. Decide what work is needed.
3. Call a tool or run a function.
4. Inspect the result.
5. Retry or choose another path if necessary.
6. Ask a human for approval when appropriate.
7. Return a final result.

LangGraph lets you define that process explicitly as a graph.

### Example: a research workflow

```text
START
  |
  v
Research
  |
  v
Evaluate quality
  |
  +---- score too low and retries remain ----> Research
  |
  +---- quality is sufficient ---------------> END
  |
  +---- retry limit reached ------------------> END
```

The important idea is that **the workflow's control flow is explicit**. You choose which steps exist, how they connect, and what conditions move execution between them.

## 2. LangChain vs LangGraph

They complement each other rather than compete.

| LangChain | LangGraph |
|---|---|
| Provides components such as chat models, prompts, tools, retrievers, and output parsers | Orchestrates steps into a stateful workflow |
| Useful for calling a model or composing components | Useful when execution needs branching, loops, state, persistence, or human approval |
| A model call may be one step | A graph can decide when and how to call the model and tools repeatedly |

A useful rule:

- **LangChain components do work.**
- **LangGraph coordinates the work.**

For example, a LangChain chat model can be called inside a LangGraph node. A LangChain tool can be executed as part of a LangGraph tool cycle.

---

## 3. The Four Building Blocks

### Graph

The overall workflow blueprint: its nodes and connections.

### Node

A unit of work. A node is usually a Python function, but it can also be a compiled subgraph.

Examples:

- Clean some text.
- Call an LLM.
- Search the web.
- Evaluate an answer.
- Ask for human approval.
- Format the final result.

A node normally receives the current state and returns a dictionary containing the fields it wants to update.

```python
def double_number(state):
    return {"number": state["number"] * 2}
```

### Edge

A connection that determines what runs next.

- A normal edge always routes to a particular node.
- A conditional edge chooses a destination based on state or other logic.

### State

The shared data carried through the workflow. It may hold user input, intermediate results, counters, messages, tool outputs, and the final answer.

A simple example:

```python
from typing import TypedDict

class NumberState(TypedDict):
    number: int
    result: str
```

A graph's state is not automatically the same thing as an LLM's conversational memory. State is data available to graph nodes; the nodes determine how that data is used.

## 4. State Schemas: `TypedDict` and Pydantic

We discussed using both `TypedDict` and Pydantic to define state.

### `TypedDict`

```python
from typing import TypedDict

class TextState(TypedDict):
    text: str
    cleaned_text: str
    word_count: int
```

`TypedDict` gives type-checking tools information about the expected dictionary shape. It does **not**, by itself, validate values at runtime.

### Pydantic `BaseModel`

```python
from pydantic import BaseModel, Field

class TextState(BaseModel):
    text: str
    cleaned_text: str = ""
    word_count: int = Field(default=0, ge=0)
```

Pydantic supports runtime validation, defaults, and constraints. For example, `ge=0` means `word_count` must be greater than or equal to zero when validation is performed.

LangGraph supports Pydantic models as state schemas, but keep two details in mind:

1. `graph.invoke(...)` commonly returns state as a dictionary.
2. Do not assume every partial node update is automatically validated exactly as you expect. Validate at the boundaries where correctness matters.

**Which should you choose?**

- Use `TypedDict` for lightweight, dictionary-oriented graph state.
- Use Pydantic when runtime validation and richer field constraints are useful.

## 5. Building and Compiling a Graph

The common graph-building pattern is:

1. Define the state schema.
2. Create a `StateGraph`.
3. Add nodes.
4. Connect nodes with edges.
5. Compile the builder.
6. Invoke or stream the compiled graph.

```python
from typing import TypedDict
from langgraph.graph import StateGraph, START, END

class NumberState(TypedDict):
    number: int

def double(state: NumberState):
    return {"number": state["number"] * 2}

builder = StateGraph(NumberState)
builder.add_node("double", double)
builder.add_edge(START, "double")
builder.add_edge("double", END)

graph = builder.compile()
result = graph.invoke({"number": 5})
print(result)  # {'number': 10}
```

### What are `START` and `END`?

They are special graph markers imported from `langgraph.graph`; they are not Python keywords.

- `START` marks where graph execution begins.
- `END` marks a terminal destination.

`compile()` turns the graph definition into a runnable graph. The builder is where you describe the workflow; the compiled graph is what you invoke.

## 6. Nodes Return Partial State Updates

One important behavior: a node usually returns **only the fields it wants to change**, not the entire state.

Suppose the current state is:

```python
{"number": 5, "name": "Alex"}
```

A node returns:

```python
{"number": 10}
```

The resulting state is effectively:

```python
{"number": 10, "name": "Alex"}
```

The `name` field remains because the node did not update it.

### Example with multiple nodes

```python
def double(state):
    return {"number": state["number"] * 2}

def add_three(state):
    return {"number": state["number"] + 3}

def format_result(state):
    return {"result": f"Final number: {state['number']}"}
```

Starting with `number = 5`:

- `double`: 5 → 10
- `add_three`: 10 → 13
- `format_result`: creates `"Final number: 13"`

This is why a node should return a dictionary of updates rather than mutate the state object and assume the mutation will be captured.

## 7. Normal Edges and Conditional Edges

### Normal edge

Use `add_edge` when the next step is always the same.

```python
builder.add_edge("clean", "analyze")
```

### Conditional edge

Use `add_conditional_edges` when the next step depends on a routing function.

```python
from typing import Literal

def route_number(state) -> Literal["high", "mid", "low"]:
    number = state["number"]

    if number > 10:
        return "high"
    elif number >= 8:
        return "mid"
    return "low"

builder.add_conditional_edges(
    "check",
    route_number,
    {
        "high": "high_node",
        "mid": "medium_node",
        "low": "low_node",
    },
)
```

The third argument is an optional **path map**. It maps labels returned by the routing function to actual node names.

The label `"mid"` does not have to match the node name `"medium_node"`—the path map connects them.

### Our threshold example

- `number > 10` → high
- `8 <= number <= 10` → medium
- `number < 8` → low

The routing function chooses the path; the destination node performs the work.

## 8. Loops, Retries, and Iteration Limits

A graph can loop back to an earlier node. This is useful for:

- Researching more when an answer is weak.
- Retrying a transiently failing operation.
- Asking an LLM to revise an answer.
- Evaluating output and improving it.

A routing function might check both quality and the attempt counter:

```python
def route_after_evaluation(state):
    if state["score"] >= 7:
        return "finish"

    if state["attempts"] < 3:
        return "research"

    return "finish"
```

In this example, quality is checked first. So if the score reaches 7 or more, the workflow finishes even if the attempt counter is at its limit.

### Keep retry logic bounded

A loop without a reliable stopping condition can continue indefinitely. Add an explicit attempt counter and a maximum. LangGraph also supports a graph-level `recursion_limit`, which acts as a safety limit on graph execution; hitting it can raise `GraphRecursionError`.

A recursion limit is a safety net, not a replacement for good routing logic.

### Three kinds of retry to distinguish

1. **Tool-level retry:** retry a failing operation, often for transient errors.
2. **Agent-level retry:** let the agent reconsider a failed tool call or try another strategy.
3. **Workflow retry:** route back to an earlier graph node based on state.

They solve related but different problems. Choose the level that matches the failure.

## 9. Reducers and Parallel Execution

LangGraph can execute independent branches in parallel when the graph structure permits it.

Example:

```text
             START
             /   \
            v     v
       Web search  Paper search
            \     /
             v   v
          Combine results
                |
               END
```

Both research branches can work independently. A downstream node can combine their results after the branches complete.

### Why reducers matter

Suppose two parallel nodes both update a shared `sources` list. Without a reducer, multiple updates to the same state key can conflict. A reducer defines how those updates are combined.

```python
import operator
from typing import Annotated, TypedDict

class ResearchState(TypedDict):
    sources: Annotated[list[str], operator.add]
```

With `operator.add`, lists are concatenated:

```python
["Web source"] + ["Paper source"]
# ['Web source', 'Paper source']
```

**Important:** concatenation does not deduplicate. If both branches return `["Source A"]`, the merged result is:

```python
["Source A", "Source A"]
```

To remove duplicates while preserving first-seen order:

```python
unique_sources = list(dict.fromkeys(state["sources"]))
```

Use reducers when multiple nodes need to update the same key in a coordinated way. A reducer is not needed for every field.

## 10. Checkpointing and Short-Term Memory

Checkpointing saves graph state as execution progresses. It enables persistence across steps and supports features such as resuming interrupted runs.

A common in-memory setup:

```python
from langgraph.checkpoint.memory import InMemorySaver

checkpointer = InMemorySaver()
graph = builder.compile(checkpointer=checkpointer)

config = {"configurable": {"thread_id": "conversation-123"}}
result = graph.invoke(input_state, config=config)
```

### What is a `thread_id`?

It identifies a conversation or workflow thread for checkpointing. Reusing a thread ID lets LangGraph locate that thread's checkpoint history.

However, **reusing a thread ID does not mean every new `invoke()` call automatically resumes the previous execution**. If you start another invocation with fresh input, you may be starting a new run. Resuming a paused execution is a different operation and depends on how the graph was interrupted and how you resume it.

### `InMemorySaver` limitations

- It is useful for demos and local learning.
- Its checkpoint data lives in process memory.
- The data is not durable across process restarts.

For a real application that needs durable checkpoints, choose a persistent checkpointer supported by your deployment.

## 11. Long-Term Memory with a Store

Checkpointing and long-term memory solve different problems.

| Concept | Purpose |
|---|---|
| Checkpointer | Saves graph state for a particular thread |
| Store | Keeps application data that can be accessed across different threads |

An in-memory store example:

```python
from langgraph.store.memory import InMemoryStore

store = InMemoryStore()

user_id = "user-123"
namespace = ("users", user_id, "memories")

store.put(
    namespace,
    "favorite_color",
    {"color": "blue"},
)

item = store.get(namespace, "favorite_color")
print(item.value)  # {'color': 'blue'}
```

### Namespace, key, and value

- **Namespace:** a logical grouping, often represented as a tuple of path-like parts.
- **Key:** the identifier of one stored item.
- **Value:** the data saved under that key.

The namespace is not necessarily a physical folder, and it is not an authorization mechanism by itself.

### Example: remember a preference across chats

A graph could save a user's favorite color in a Store. A later conversation with the same `user_id` can retrieve it even if it uses a different `thread_id`, provided the application looks up the same namespace and key.

Using a different user ID or looking up a key that was never saved will not magically retrieve that preference.

`InMemoryStore` is for learning and testing; its data is not durable across process restarts. Also, a Store does not automatically give an LLM memory. Your graph needs logic to save, retrieve, and include relevant information when appropriate.

## 12. Human-in-the-Loop

Some decisions should be made or approved by a person—for example, sending an email, publishing a post, or performing a consequential action.

LangGraph supports interrupting execution, waiting for input, and resuming the graph.

Conceptually:

```text
Prepare action
     |
     v
Pause for approval
     |
     +---- approved ----> Perform action
     |
     +---- rejected ----> Stop or revise
```

The common pieces are:

- `interrupt(...)` — pause execution and surface a request for input.
- A checkpointer — persist the graph's state while paused.
- `Command(resume=...)` — resume the interrupted graph with a response.
- The same `thread_id` — identify the interrupted thread when resuming.

### Boolean decisions

This expression:

```python
decision == "approve"
```

evaluates to a Boolean: `True` if `decision` equals `"approve"`, otherwise `False`.

So a node can return:

```python
return {"approved": decision == "approve"}
```

That is a partial state update setting the `approved` field.

**Safety note:** in a demo, simulate actions such as sending an email. In a real application, put a clear approval boundary before consequential side effects and handle rejection explicitly.

## 13. Streaming

Streaming lets an application receive information while a graph runs instead of waiting only for the final result.

### `invoke()`

```python
result = graph.invoke(input_state)
```

Returns the final result after the graph run completes.

### `stream(..., stream_mode="updates")`

```python
for update in graph.stream(input_state, stream_mode="updates"):
    print(update)
```

Yields node-level updates as graph steps execute.

### `stream(..., stream_mode="values")`

```python
for snapshot in graph.stream(input_state, stream_mode="values"):
    print(snapshot)
```

Yields full state snapshots after steps.

### Model-token streaming

A subtle but important distinction: graph streaming does not automatically make a normal model call stream tokens. If a node uses:

```python
response = llm.invoke(messages)
```

the node waits for the complete model response before returning its update. For incremental LLM output, use the model's streaming API and consume its chunks, or use the appropriate LangGraph message-streaming mode with a streaming-capable model.

In short:

- **Graph updates** show progress between nodes.
- **Model token streaming** shows the LLM's response arriving incrementally.

They are related, but not the same.

## 14. Subgraphs

A subgraph is a compiled graph used as a component inside another graph. It helps organize large workflows into reusable pieces.

Example:

```text
Parent graph:
START -> Research subgraph -> Finalize answer -> END

Research subgraph:
          START
          /   \
         v     v
       Web    Papers
         \     /
          v   v
         Combine
            |
           END
```

You can build and compile the research graph separately, then register it as a node in the parent graph:

```python
research_graph = research_builder.compile()

parent_builder = StateGraph(ResearchState)
parent_builder.add_node("research", research_graph)
parent_builder.add_node("finalize", create_final_answer)
parent_builder.add_edge(START, "research")
parent_builder.add_edge("research", "finalize")
parent_builder.add_edge("finalize", END)

parent_graph = parent_builder.compile()
```

The parent graph can then use fields produced by the subgraph—for example, a `summary` field—to create the final answer.

Subgraphs are useful for modularity, reuse, and keeping a complex graph understandable.

## 15. LLM Tool Calling and `ToolNode`

A tool-using agent combines a model with executable functions.

The typical cycle is:

```text
User message
     |
     v
Assistant / LLM
     |
     +---- tool call requested ----> ToolNode executes tool
     |                                   |
     |                                   v
     |                              Tool result
     |                                   |
     +<----------------------------------+
     |
     +---- no tool call ----------------> END
```

### The key pieces

- `@tool` defines a tool with a name, schema, and description.
- `llm.bind_tools(tools)` makes tool definitions available to a compatible model.
- `ToolNode(tools)` executes requested tool calls.
- `tools_condition` checks whether the latest assistant message contains tool calls and routes accordingly.
- The assistant node runs again after the tool result so the model can interpret it or request another tool.

Example:

```python
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode, tools_condition

@tool
def multiply(a: int, b: int) -> int:
    """Multiply two integers."""
    return a * b

tools = [multiply]
```

The model must support tool calling through the integration you use. A tool being defined in Python does not, by itself, make the model execute it.

### Our arithmetic example

We used `multiply`, `divide`, and `add` tools with a local Ollama model:

1. Multiply `1401 * 1041` → `1,458,441`
2. Divide by `1111` using integer floor division (`//`) → `1312`
3. Add `1000` → `2312`

The result is `2312` because the divide tool used integer floor division, not regular floating-point division. Tool implementations determine the actual arithmetic semantics.

## 16. Tool Errors and Reliable Agent Behavior

We explored what happens when a tool fails, including division by zero.

A tool can return an error message, raise an exception, or have the tool node handle the exception, depending on how it is implemented and configured.

One important lesson from our test: **an error message does not guarantee that the model will stop or behave the way you intended**. After receiving an error, an LLM may try another action, give up, or even return an earlier intermediate result as if it were final.

For reliable behavior:

1. Validate tool inputs.
2. Make error results clear and structured.
3. Decide which failures are retryable.
4. Set a retry limit.
5. Track errors or success in graph state when the workflow must enforce a rule.
6. Route explicitly after critical failures rather than relying only on the LLM's judgment.
7. Never treat an intermediate calculation as the final result unless the workflow verifies that all required steps succeeded.

### Three levels of error handling

- **Tool-level:** catch or retry errors inside the tool.
- **ToolNode-level:** configure how tool exceptions are handled.
- **Graph-level:** store status/error information and use conditional edges to control what happens next.

For deterministic requirements, explicit state and routing are more dependable than instructions in a prompt alone.

## 17. Reusable Tools and Configuration

As a project grows, avoid placing every tool, model setting, and graph definition in one large file.

A simple structure:

```text
project/
├── .env
├── config.py
├── model.py
├── tools.py
├── graph.py
└── main.py
```

Possible responsibilities:

- `config.py`: central configuration such as the model name.
- `model.py`: creates and configures the chat model.
- `tools.py`: contains reusable tool functions.
- `graph.py`: defines nodes, edges, routing, and graph compilation.
- `main.py`: runs the application.
- `.env`: local environment values and secrets.

Use one source of truth for configuration where practical. Keep secrets out of source control, add `.env` to `.gitignore`, and provide a `.env.example` with placeholder values if needed.

For our local setup, the model name was configured as:

```python
MODEL = "llama3.2:3b"
```

The exact model and tool-calling behavior depend on your local Ollama setup and the installed LangChain integration. Test the complete tool cycle rather than assuming that all models behave identically.

---

## 18. Common Confusions We Resolved

### “The model printed JSON. Why didn't `tools_condition` route to the tool?”

Because JSON-looking text in `response.content` is not the same as a structured tool call. `tools_condition` checks the assistant message's tool-call data, typically `response.tool_calls`.

If the model merely prints something like:

```json
{"name": "multiply", "arguments": {"a": 2, "b": 3}}
```

as ordinary text, the graph may treat it as a normal assistant response rather than a request for tool execution.

**Fix:** use a model/integration that supports structured tool calling, bind the tools correctly, and give the model clear instructions. Inspect `response.tool_calls` while debugging.

### “Why did the model stop after a tool error?”

The LLM decides what to do with the result it receives unless the graph enforces a specific route. Model behavior can vary. Use explicit error state and routing when a failure must prevent later steps.

### “Does the same `thread_id` always resume my last invocation?”

No. It identifies the thread's checkpoint history, but a new `invoke()` with fresh input can start a new run. Resuming an interrupted run requires the appropriate resume flow.

### “Does checkpointing automatically give the LLM memory?”

No. Checkpointing saves graph state. The graph must retrieve and provide relevant data to the model. Long-term user information may be stored separately in a Store.

### “Does `operator.add` remove duplicate sources?”

No. It concatenates lists. Deduplication is a separate step.

### “Does `graph.stream()` mean I get every model token?”

Not necessarily. It depends on the stream mode and whether the model call itself is streaming.

### “Does a tool error always stop the graph?”

No. The error may be converted to a result, handled by the tool node, or propagated. The model may continue unless the graph routes explicitly.

### “Are `TypedDict` and Pydantic identical?”

No. `TypedDict` primarily describes expected dictionary types for static tooling; Pydantic can validate values at runtime when validation is performed.

---

## 19. A Mental Model to Keep

Think of LangGraph as a **state machine with explicit control flow**.

- **State** is the data carried through the workflow.
- **Nodes** read state and return updates.
- **Edges** decide what executes next.
- **Conditional edges** make decisions.
- **Reducers** combine concurrent updates to shared keys.
- **Checkpointers** save per-thread graph progress.
- **Stores** keep data that can be accessed across threads.
- **Interrupts** let humans participate in execution.
- **Streaming** exposes progress or incremental model output.
- **Subgraphs** package reusable workflows.
- **Tool nodes** execute model-requested tools.
- **Explicit error state and routing** make critical behavior more predictable.

A useful design question for every graph is:

> What state do I need, what can each node change, and what exact condition determines the next step?

If you can answer those three questions, you're thinking in LangGraph's terms.

---

## 20. Practice Questions

Try answering these without looking at the answers first.

### Questions

1. What is the difference between a node and an edge?
2. If a node returns `{"score": 8}`, what happens to other state keys it did not update?
3. What does `START` represent? What does `END` represent?
4. What is the purpose of the third argument to `add_conditional_edges`?
5. A loop retries while `attempts < 3`. Why should the graph also have a reliable stopping condition?
6. Two parallel nodes return `["A"]` and `["B"]`. What does `Annotated[list[str], operator.add]` do?
7. If both parallel nodes return `["A"]`, will `operator.add` remove the duplicate?
8. What is the difference between a checkpointer and a Store?
9. Why doesn't reusing a `thread_id` automatically mean a new `invoke()` resumes an interrupted run?
10. What does `tools_condition` look for when deciding whether to route to `ToolNode`?
11. Why might an LLM continue after a tool returns an error?
12. What is the difference between graph-update streaming and model-token streaming?

<details>
<summary><strong>Answer key</strong></summary>

1. A node performs work; an edge connects steps and controls execution order.
2. Those other keys remain unchanged; the returned dictionary is a partial update.
3. `START` is the entry marker; `END` is the terminal marker.
4. It maps routing labels returned by the routing function to destination node names.
5. To prevent unbounded execution and ensure the workflow can terminate predictably.
6. It concatenates the lists, producing `["A", "B"]`.
7. No. It produces `["A", "A"]`; deduplicate separately if required.
8. A checkpointer saves graph state for a thread; a Store holds data that can be retrieved across threads.
9. A new invocation with fresh input can start a new run; resuming a paused execution needs the appropriate resume operation and thread configuration.
10. It checks whether the latest assistant message contains structured tool calls.
11. The LLM decides how to respond to the error unless the graph explicitly enforces a route.
12. Graph-update streaming reports graph progress; model-token streaming emits chunks of the model's response as they arrive.

</details>

---

## Suggested Next Step

Build one small agent that combines several concepts:

1. Accept a user request.
2. Use a model with one or two tools.
3. Track attempts and tool errors in state.
4. Route conditionally after tool execution.
5. Add a checkpoint.
6. Stream graph updates.
7. Add a human approval step before a simulated consequential action.

Once that feels comfortable, the next phase—**MCP (Model Context Protocol)**—will make more sense: LangGraph manages your agent's workflow, while MCP standardizes how an application can connect to tools and context exposed by MCP servers.

---

*This guide is a learning reference, not a guarantee that every code snippet is a complete production application. LangGraph and integration APIs evolve, so check the documentation for the versions installed in your environment.*
