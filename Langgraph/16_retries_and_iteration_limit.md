# 16. Retries and Iteration Limits in LangGraph

> Notes for learning LangGraph with Python, LangChain, and Ollama.

## Learning goals

By the end of this lesson, you should be able to:

-   Distinguish tool-level retries from agent-level retries.
-   Handle predictable tool errors and exceptions.
-   Configure `ToolNode` error handling.
-   Limit graph execution with `recursion_limit`.
-   Design explicit stopping conditions for an agent.

------------------------------------------------------------------------

## 1. Three different concepts

  -----------------------------------------------------------------------
  Concept                 What it controls        Example
  ----------------------- ----------------------- -----------------------
  **Error handling**      What happens when an    Return a useful error
                          operation fails         message

  **Tool-level retry**    How many times one      Retry a temporary API
                          operation is attempted  timeout

  **Agent-level retry**   Whether the LLM should  The model changes
                          try a tool call again   arguments after an
                                                  error

  **Graph iteration       How long the graph may  Stop a repeated
  limit**                 continue executing      assistant--tool loop
  -----------------------------------------------------------------------

A retry is not the same as error handling. Handling an error can let the
graph continue without retrying anything.

## 2. Handle predictable errors inside a tool

A tool can return a clear error result for an expected, recoverable
situation.

``` python
from langchain_core.tools import tool


@tool
def divide(a: float, b: float) -> float | str:
    """Divide a by b. Return an error message if b is zero."""
    if b == 0:
        return "Error: Cannot divide by zero."

    return a / b
```

Calling this tool with `b=0` returns a string. It does **not** raise an
exception.

That means the tool invocation itself completed and the LLM can inspect
the returned error text. The model may explain it, ask for new input, or
choose another action.

### Raising an exception instead

``` python
@tool
def divide(a: float, b: float) -> float:
    """Divide a by b."""
    if b == 0:
        raise ValueError("Cannot divide by zero.")

    return a / b
```

Now division by zero raises a real exception. The graph's tool execution
needs to handle it if you want the workflow to recover.

## 3. Handle exceptions with `ToolNode`

LangGraph's `ToolNode` supports error handling:

``` python
from langgraph.prebuilt import ToolNode

tool_node = ToolNode(
    tools=[divide],
    handle_tool_errors=True,
)
```

With `handle_tool_errors=True`, tool exceptions can be converted into
tool error messages that the model can inspect, rather than immediately
propagating out of the tool node.

Error handling alone does **not** automatically retry the operation. The
model might decide to try again, stop, or give an explanation.

You can customize the error-handling behavior when you need more
specific messages or policies. Check the API documentation for the
installed LangGraph version if you use a custom handler.

## 4. Tool-level retries

Tool-level retries happen inside the function or service wrapper. They
are most useful for transient failures, such as temporary network errors
or rate limits.

A simple simulation:

``` python
def fetch_data():
    for attempt in range(1, 4):
        print(f"Attempt {attempt}")

        # Replace this condition with a real API request
        # and catch its specific transient exception.
        if attempt == 3:
            return "Data fetched successfully!"

    raise RuntimeError("Fetching failed after 3 attempts.")
```

This simulates three attempts. It is not production-ready retry logic
because it does not actually catch a network exception or wait between
attempts.

### Using Tenacity

Install the library if needed:

``` bash
pip install tenacity
```

Example:

``` python
from tenacity import retry, stop_after_attempt, wait_exponential


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=4),
)
def fetch_from_api():
    # Replace with the actual API request.
    # Raise an exception when the request fails.
    return call_external_api()
```

-   `stop_after_attempt(3)` allows at most three attempts.
-   `wait_exponential(...)` adds increasing delays between attempts.
-   If all attempts fail, the final exception propagates unless you
    configure a fallback.

In real applications, retry only appropriate transient errors. Repeating
an invalid request or a permission error usually will not help. Be
especially careful retrying operations that create side effects, such as
sending an email or making a payment.

## 5. Agent-level retries

An agent-level retry happens when the error is returned to the LLM and
the model chooses to make another tool call.

For example:

1.  The assistant calls `divide(a=100, b=0)`.
2.  The tool returns an error message.
3.  The assistant receives that tool result.
4.  The model may explain the error, request new input, or try a
    different action.

The LLM's decision is not a guaranteed retry policy. If you require a
strict number of attempts, implement an explicit counter and routing
condition in the graph.

## 6. Protect the graph with `recursion_limit`

A tool-calling graph commonly contains this loop:

``` python
builder.add_edge("tools", "assistant")
```

This returns tool results to the assistant so it can decide what to do
next. It is essential for many agents, but a model could keep requesting
tools.

Use a recursion limit when invoking the graph:

``` python
from langgraph.errors import GraphRecursionError

try:
    result = graph.invoke(
        {"messages": messages},
        config={"recursion_limit": 10},
    )
except GraphRecursionError:
    print("Agent stopped: graph execution limit reached.")
```

`messages` should be your prepared list of LangChain messages.

### Important details

-   `recursion_limit` limits graph **supersteps**, not exactly the
    number of LLM calls or tool calls.
-   A tool-calling cycle can use multiple supersteps.
-   When the limit is exceeded, LangGraph raises `GraphRecursionError`.
-   Catching that exception lets the application log the event or return
    a controlled fallback.
-   The limit does not force the LLM to generate a final answer.

Use it as a safety guard, not as your only stopping strategy.

## 7. Explicitly count attempts or tool executions

For precise policies, add a counter to state and route based on it. For
example, a simple workflow can stop after three attempts:

``` python
from typing import TypedDict
from langgraph.graph import StateGraph, START, END


class AgentState(TypedDict):
    attempts: int
    answer: str


def attempt_task(state: AgentState):
    next_attempt = state["attempts"] + 1
    return {
        "attempts": next_attempt,
        "answer": f"Attempt {next_attempt}",
    }


def route_after_attempt(state: AgentState):
    if state["attempts"] >= 3:
        return END
    return "attempt_task"


builder = StateGraph(AgentState)
builder.add_node("attempt_task", attempt_task)
builder.add_edge(START, "attempt_task")
builder.add_conditional_edges("attempt_task", route_after_attempt)

graph = builder.compile()

result = graph.invoke({
    "attempts": 0,
    "answer": "",
})

print(result)
```

This small graph demonstrates a counter-based stopping condition. In a
real tool-calling graph, increment the counter at the point that matches
your policy---for example, when the assistant requests a tool or when a
tool execution fails.

Think carefully about what the counter means:

-   Total tool calls?
-   Failed tool calls only?
-   Attempts per individual tool?
-   LLM reasoning turns?
-   Whole graph steps?

Choose one definition and name the state field accordingly, such as
`tool_call_count` or `failed_attempts`.

## 8. Recommended design

A robust tool-using agent often combines these layers:

1.  Validate inputs and handle predictable errors in the tool.
2.  Retry transient failures inside the tool, with a small maximum and
    appropriate delays.
3.  Return useful error information to the model when reasoning can
    help.
4.  Track tool calls or failed attempts explicitly when you need a
    strict budget.
5.  Set `recursion_limit` as a final graph-level safeguard.
6.  Log failures without leaking secrets or sensitive data.

## 9. Quick knowledge check

**Question:** What does `ToolNode(tools, handle_tool_errors=True)`
primarily do?

-   A. Retries every tool exactly three times.
-   B. Handles tool exceptions so they can be returned as error
    messages.
-   C. Converts division by zero into zero.
-   D. Prevents the LLM from calling tools.

**Answer:** B. Error handling and retrying are separate behaviors.

**Question:** What happens if a graph exceeds its configured
`recursion_limit`?

**Answer:** LangGraph raises `GraphRecursionError`; it does not
automatically force a final answer.

------------------------------------------------------------------------

## Key takeaways

-   A returned error string is a normal tool result; a raised exception
    is an exception.
-   `ToolNode` error handling does not itself guarantee retries.
-   Tool-level retries are suited to transient failures.
-   Agent-level retries depend on the model unless explicitly
    controlled.
-   `recursion_limit` is a graph execution safeguard, not an exact
    tool-call counter.
-   Explicit counters and conditional routes provide more precise
    control.

## Next lesson

**Reusable tools and configurations** --- organize tool definitions,
model settings, graph construction, and application entry points into
reusable Python modules before integrating MCP.
