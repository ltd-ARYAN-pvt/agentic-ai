# 17. Reusable Tools and Configurations in LangGraph

> Notes for organizing a LangGraph project using Python, LangChain, and
> Ollama.

## Learning goals

By the end of this lesson, you should be able to:

-   Separate tool definitions from graph logic.
-   Reuse the same tools across multiple agents.
-   Keep model settings in a central configuration module.
-   Create a reusable model factory.
-   Separate graph construction from application execution.
-   Understand how this structure prepares a project for MCP.

------------------------------------------------------------------------

## 1. Why organize the project?

For a small experiment, one file containing tools, model setup, graph
nodes, edges, and invocation code is perfectly reasonable.

As the project grows, separating responsibilities makes it easier to
test and maintain:

-   **Tools:** what the agent can do.
-   **Configuration:** which model and settings to use.
-   **Model factory:** how to construct the chat model.
-   **Graph:** how the agent is orchestrated.
-   **Main entry point:** how the application is run.

## 2. Suggested project structure

``` text
langgraph_agent/
├── tools.py
├── config.py
├── model.py
├── graph.py
└── main.py
```

Run `main.py` from the project directory so imports such as
`from tools import TOOLS` resolve as expected.

For larger projects, you may turn this directory into a Python package
and add tests, prompts, schemas, and service modules.

## 3. Define reusable tools in `tools.py`

``` python
from langchain_core.tools import tool


@tool
def multiply(a: int, b: int) -> int:
    """Multiply two integers."""
    return a * b


@tool
def divide(a: float, b: float) -> float:
    """Divide a by b."""
    if b == 0:
        raise ValueError("Cannot divide by zero.")
    return a / b


@tool
def add(a: float, b: float) -> float:
    """Add two numbers."""
    return a + b


TOOLS = [multiply, divide, add]
```

### Reuse a tool directly

``` python
from tools import multiply

result = multiply.invoke({"a": 12, "b": 5})
print(result)  # 60
```

The `@tool` decorator turns a Python function into a LangChain tool
object with a name, description, and input schema. It can be invoked
directly, bound to a compatible chat model, or supplied to a LangGraph
`ToolNode`.

### Reuse tools across agents

``` python
# calculator_agent.py
from tools import TOOLS

# research_agent.py
from tools import add, multiply
```

Each agent imports the same definitions instead of maintaining
duplicated implementations. This improves consistency and makes it
easier to update and test the tools.

## 4. Centralize model settings in `config.py`

``` python
MODEL_NAME = "llama3.2:3b"
TEMPERATURE = 0
```

Keeping settings in one place makes changing the model easier.
Configuration can later include timeouts, endpoint URLs, or other
non-secret settings.

Do not put API keys, passwords, or other secrets directly in source
code. Use environment variables or a suitable secrets manager when
secrets are required.

## 5. Create a reusable model factory in `model.py`

``` python
from langchain_ollama import ChatOllama
from config import MODEL_NAME, TEMPERATURE


def get_model():
    return ChatOllama(
        model=MODEL_NAME,
        temperature=TEMPERATURE,
    )
```

Now every agent can use the same model-construction function:

``` python
from model import get_model
from tools import TOOLS

llm = get_model().bind_tools(TOOLS)
```

The factory makes model setup consistent and gives you one place to
change initialization behavior.

## 6. Build the graph in `graph.py`

``` python
from langchain_core.messages import SystemMessage
from langgraph.graph import StateGraph, START, MessagesState
from langgraph.prebuilt import ToolNode, tools_condition

from model import get_model
from tools import TOOLS


SYSTEM_PROMPT = """
You are a helpful calculation assistant.
Use the available tools for arithmetic.
Use each result in the next requested operation.
If a tool fails, explain the error honestly.
Do not invent tool results.
"""


def build_graph():
    llm = get_model().bind_tools(TOOLS)

    def assistant(state: MessagesState):
        # Prepend the system prompt for this model invocation.
        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            *state["messages"],
        ]
        response = llm.invoke(messages)
        return {"messages": [response]}

    builder = StateGraph(MessagesState)
    builder.add_node("assistant", assistant)
    builder.add_node(
        "tools",
        ToolNode(TOOLS, handle_tool_errors=True),
    )

    builder.add_edge(START, "assistant")
    builder.add_conditional_edges("assistant", tools_condition)
    builder.add_edge("tools", "assistant")

    return builder.compile()
```

### Understand the graph

-   `build_graph()` constructs and compiles the workflow.
-   `get_model().bind_tools(TOOLS)` exposes the tool schemas to the
    model.
-   `assistant` asks the model what to do next.
-   `ToolNode` executes structured tool calls.
-   `tools_condition` routes to the tool node when the latest assistant
    message requests tools; otherwise, it routes to the end.
-   The edge from `tools` back to `assistant` allows the model to
    inspect tool results and continue.

**Note:** This example prepends the system prompt on every assistant
invocation rather than storing it in graph state. For a larger
application, consider a dedicated prompt-management approach and avoid
duplicating system messages if you choose to keep them in state.

`handle_tool_errors=True` handles tool exceptions; it does not implement
an automatic retry policy by itself.

## 7. Run the agent from `main.py`

``` python
from langchain_core.messages import HumanMessage
from graph import build_graph


def main():
    graph = build_graph()

    result = graph.invoke(
        {
            "messages": [
                HumanMessage(
                    content=(
                        "Multiply 1401 by 1041, "
                        "then add 1000. Use the tools."
                    )
                )
            ]
        },
        config={"recursion_limit": 10},
    )

    print(result["messages"][-1].content)


if __name__ == "__main__":
    main()
```

Run the application:

``` bash
python main.py
```

The exact result depends on the requested calculation and the behavior
of the configured model. For the example above, the expected arithmetic
result is `1459441`.

## 8. What belongs where?

  File          Responsibility
  ------------- ----------------------------------------------------
  `tools.py`    Tool implementations and the exported tool list
  `config.py`   Model name and other non-secret settings
  `model.py`    Model initialization
  `graph.py`    State, nodes, edges, prompt use, graph compilation
  `main.py`     User input, invocation, and output

Keep this separation practical rather than absolute. For a tiny
experiment, one file is fine. Split modules when it improves clarity or
reuse.

## 9. How this prepares you for MCP

  -----------------------------------------------------------------------
  Local tool setup                    MCP-based setup
  ----------------------------------- -----------------------------------
  Tools are defined as Python         Tools may be exposed by an external
  functions in your project.          MCP server.

  The application imports tool        An MCP client discovers tools from
  objects directly.                   a server.

  `ToolNode` executes local LangChain An MCP adapter/client communicates
  tools.                              with the server and exposes tools
                                      for agent use.

  LangGraph controls the              LangGraph can still control the
  assistant--tool workflow.           workflow.
  -----------------------------------------------------------------------

MCP does not replace LangGraph. It standardizes how applications
discover and interact with tools and other context exposed by MCP
servers.

## 10. Quick knowledge check

**Question:** Two agents need the same `multiply` tool. What is the main
benefit of defining it once in `tools.py`?

-   A. Each agent automatically receives an isolated copy of the
    implementation.
-   B. Both agents can import and reuse the same tool definition.
-   C. Python converts the tool into an MCP server automatically.
-   D. The tool no longer needs validation or error handling.

**Answer:** B. Shared modules avoid duplicated implementations and
simplify maintenance.

------------------------------------------------------------------------

## Key takeaways

-   Define each reusable tool once and import it wherever needed.
-   Centralize model settings in a configuration module.
-   Use a model factory for consistent initialization.
-   Keep graph orchestration separate from application invocation.
-   Keep secrets out of source code.
-   MCP can provide tools from external servers while LangGraph
    continues to orchestrate the agent.

## Next: MCP fundamentals

Start with the problem MCP solves, then learn the **host, client,
server, tools, resources, and prompts** before building a Python MCP
server and connecting it to a LangGraph agent.
