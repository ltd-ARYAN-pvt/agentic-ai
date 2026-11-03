# MCP — Lesson 1: Foundations, Architecture, and the Big Picture 🚀

> **Goal:** Understand what MCP is, why it exists, how its architecture works, and how it fits with Python, APIs, LangChain, and LangGraph—before writing our first MCP server.

This lesson is based on our learning journey and examples. It is designed as a visual, easy-to-revisit reference: use the diagrams, follow the request flows, and test your understanding at the end.

## Learning objectives

By the end of this lesson, you should be able to:
- Explain the problem MCP solves.
- Distinguish the **Host**, **Client**, and **Server**.
- Explain the difference between **Tools**, **Resources**, and **Prompts**.
- Compare MCP with Python functions, LangChain tools, and REST APIs.
- Trace a request from a user question to a tool result and back.
- Explain how MCP and LangGraph complement each other.

## Contents

1. [Why MCP exists](#1-why-mcp-exists)
2. [What MCP is—and isn't](#2-what-mcp-isand-isnt)
3. [The architecture: Host, Client, Server](#3-the-architecture-host-client-server)
4. [The three capability types](#4-the-three-capability-types)
5. [Python functions vs LangChain tools vs REST APIs vs MCP](#5-python-functions-vs-langchain-tools-vs-rest-apis-vs-mcp)
6. [A complete MCP request flow](#6-a-complete-mcp-request-flow)
7. [Where LangGraph fits](#7-where-langgraph-fits)
8. [Local and remote servers](#8-local-and-remote-servers)
9. [Security and practical boundaries](#9-security-and-practical-boundaries)
10. [The mental model](#10-the-mental-model)
11. [Quick revision](#11-quick-revision)
12. [Knowledge check](#12-knowledge-check)
13. [Mini challenge](#13-mini-challenge)
14. [What's next](#14-whats-next)

---

# 1. Why MCP exists

Imagine you build several AI applications:

- A coding assistant.
- A research agent.
- A customer-support bot.
- A personal productivity assistant.

Now imagine they all need access to the same systems: files, databases, GitHub, calendars, or internal APIs.

### Without a common protocol

Each application may need custom integration logic for each service.

```text
Coding Assistant ───── custom code ───── Files
Research Agent ─────── custom code ───── Files
Support Bot ────────── custom code ───── Files

Coding Assistant ───── custom code ───── Database
Research Agent ─────── custom code ───── Database
Support Bot ────────── custom code ───── Database
```

Every new application or service can add more integration work. The code, assumptions, and error handling may differ from one integration to another.

### With MCP

MCP provides a common protocol for applications to discover and interact with capabilities exposed by MCP servers.

```text
┌─────────────────────┐
│  Coding Assistant   │──┐
└─────────────────────┘  │    ┌──────────────────┐
┌─────────────────────┐  ├───▶│  Files MCP Server│──▶ Files
│   Research Agent    │──┤    └──────────────────┘
└─────────────────────┘  │
┌─────────────────────┐  │    ┌──────────────────┐
│   Support Bot       │──┴───▶│ Database MCP     │──▶ Database
└─────────────────────┘       │ Server           │
                              └──────────────────┘
```

Each application still needs an MCP client and appropriate integration, but the communication contract is standardized. The server can expose its capabilities in a way compatible MCP clients understand.

> **Core idea:** MCP standardizes how an AI application connects to tools and context from external systems.

MCP does not automatically make an LLM more intelligent. It gives the surrounding application a standard way to connect the model-driven workflow to capabilities beyond the model.

---

# 2. What MCP is—and isn't

**MCP** stands for **Model Context Protocol**.

It is an open protocol for communication between AI applications and servers that expose capabilities such as tools, resources, and prompts.

### MCP is
- A common protocol and capability-discovery mechanism.
- A way for applications to interact with compatible servers.
- Useful for connecting AI applications to local or remote systems.
- Independent of any single model provider or agent framework.

### MCP is not
- An LLM or a model-training technique.
- A replacement for Python.
- A replacement for LangChain or LangGraph.
- A guarantee that every model can use tools correctly.
- A security or authorization system that removes the need for safeguards.

### A simple analogy

Think about a standardized charging connector.

- The device is the application.
- The connector defines how the connection works.
- The accessory provides a capability.

MCP plays a similar standardization role for software communication. The analogy is imperfect—MCP also defines structured messages and capability semantics—but it captures why a shared interface is useful.

---

# 3. The architecture: Host, Client, Server

MCP has three key roles. Understanding their boundaries is essential.

## 3.1 Host — the main AI application

The **host** is the application the user interacts with. It manages the model interaction and MCP clients, and controls how server capabilities are made available to the application.

Examples might include a desktop AI application or your own Python application orchestrated with LangGraph.

## 3.2 Client — the protocol connection

An **MCP client** is a component within the host that communicates with an MCP server using the MCP protocol.

A host can manage multiple clients, commonly one client connection per server.

## 3.3 Server — the capability provider

An **MCP server** exposes capabilities to clients. It might read approved files, query a database, call an API, or provide reusable prompt templates.

The server can be a local process or a remote service.

## Architecture illustration

```text
                    USER
                      │
                      ▼
        ┌────────────────────────────┐
        │          MCP HOST          │
        │  AI app + model + policy   │
        │                            │
        │  ┌──────────┐ ┌──────────┐ │
        │  │ Client A │ │ Client B │ │
        │  └────┬─────┘ └────┬─────┘ │
        └───────┼─────────────┼───────┘
                │             │
           MCP protocol  MCP protocol
                │             │
                ▼             ▼
        ┌──────────────┐ ┌──────────────┐
        │ Files MCP    │ │ Database MCP │
        │ Server       │ │ Server       │
        └──────┬───────┘ └──────┬───────┘
               │                │
               ▼                ▼
           Approved files   Database
```

### Remember the roles

| Role | Responsibility | Mental shortcut |
|---|---|---|
| Host | Runs/manages the AI application and clients | The application |
| Client | Communicates with a server over MCP | The connector |
| Server | Exposes capabilities and handles requests | The provider |

**Important:** the MCP server does not have to be a separate physical computer. A local server process can communicate with a client over standard input/output (stdio).

---

# 4. The three capability types

MCP servers can expose three important capability types: **Tools, Resources, and Prompts**.

## 4.1 Tools — “Do something”

Tools expose executable operations that an AI application can discover and invoke.

Examples:
- `search_lessons(query)`
- `calculate(expression)`
- `query_database(...)`
- `create_issue(...)`

A tool typically has a name, description, and input schema. A client can discover tools, and a host may make the available tool information accessible to its model.

```text
Model/application decides a tool is useful
                    │
                    ▼
             tools/call request
                    │
                    ▼
             MCP server runs it
                    │
                    ▼
               Tool result
```

Tools may have side effects. A tool that sends an email, deletes a file, or changes a database needs appropriate permissions and safeguards.

## 4.2 Resources — “Give me information”

Resources expose data or context, typically identified by URIs.

Examples:
- `file:///project/README.md`
- `docs://project/architecture`
- `db://customers/schema`

A resource can let the application read a document, schema, or other information and decide how to provide that context to the model.

```text
Application needs context
          │
          ▼
   Select/read resource
          │
          ▼
     Resource content
          │
          ▼
 Application uses context
```

Resources are generally application-controlled: the host decides how to present or include them in the model's context. A resource is not simply a tool with a different name.

## 4.3 Prompts — “Use these instructions”

Prompts expose reusable prompt templates, potentially with arguments.

Examples:
- `review_python_code(code)`
- `summarize_document(document_name)`
- `quiz_from_lesson(topic)`

A prompt template provides reusable instructions. It does not, by itself, execute Python or call an external API.

```text
User/application selects prompt
              │
              ▼
        prompts/get
              │
              ▼
   Template + supplied arguments
              │
              ▼
     Application/model uses it
```

## One project, all three

Imagine an MCP server for your LangGraph learning repository.

| Capability | Example | Purpose |
|---|---|---|
| Tool | `search_lessons("checkpointing")` | Searches files and returns matches |
| Resource | `lesson://langgraph/checkpointing` | Exposes lesson content to read |
| Prompt | `quiz_from_lesson(topic="MCP")` | Supplies a reusable quiz prompt |

The distinctions are useful design heuristics, not absolute restrictions. A tool can return data, and a resource can support a tool-driven workflow.

## Protocol operation names

At a high level, the client can use these protocol methods:

| Capability | Discover/list | Use/read/get |
|---|---|---|
| Tools | `tools/list` | `tools/call` |
| Resources | `resources/list` | `resources/read` |
| Prompts | `prompts/list` | `prompts/get` |

These are MCP protocol methods. An SDK handles much of the message-formatting and protocol machinery for you.

---

# 5. Python functions vs LangChain tools vs REST APIs vs MCP

These concepts work at different levels and can be combined.

## Python function

A function is code that your Python program calls directly.

```python
def multiply(a: int, b: int) -> int:
    return a * b

print(multiply(6, 7))  # 42
```

It does not automatically provide a standard interface for other applications.

## LangChain tool

A LangChain tool wraps an operation in an interface that an agent can use. It commonly provides a name, description, and input schema.

```python
from langchain_core.tools import tool

@tool
def multiply(a: int, b: int) -> int:
    """Multiply two integers."""
    return a * b
```

A compatible model may request a tool call, and the application or agent executes it. Defining the tool alone does not guarantee that every model will call it correctly.

## REST API

A REST API provides an HTTP interface to a service.

For example:

```http
GET /products/42
```

The server might return JSON containing the product. REST is an architectural style; HTTP is the transport commonly used by REST APIs.

## MCP

MCP defines a standard protocol for applications to discover and interact with capabilities exposed by MCP servers.

An MCP server might expose a `get_product` tool whose implementation calls a REST API or a Python function.

### Comparison table

| Question | Python function | LangChain tool | REST API | MCP |
|---|---|---|---|---|
| Main role | Execute code | Expose an operation to an agent | Provide a service interface over HTTP | Standardize AI capability access |
| Common discovery protocol? | No | Framework/configuration dependent | API documentation or other discovery | MCP capability discovery |
| Can connect separate processes? | Not by a direct function call alone | Depends on implementation | Yes | Yes |
| Defines Tools, Resources, Prompts as MCP primitives? | No | Not by default | Not inherently | Yes |

### How they can fit together

```text
LangGraph workflow
       │
       ▼
LangChain tool / MCP adapter
       │
       ▼
MCP client
       │
       ▼
MCP server
       │
       ▼
Python function ───────► REST API ───────► External service
```

This is one possible design, not a mandatory stack. An MCP server could query a database directly instead of calling a REST API.

> **Remember:** Python functions perform operations; LangChain tools expose operations to an agent; REST APIs provide HTTP service interfaces; MCP standardizes communication between AI applications and MCP servers.

---

# 6. A complete MCP request flow

Let's trace an example from start to finish.

### User request

> “Find my lesson about checkpointing and summarize the key concept.”

Assume an MCP server exposes `search_lessons`.

## Step-by-step flow

```text
┌───────────────────────────────┐
│ 1. User asks a question       │
└───────────────┬───────────────┘
                ▼
┌───────────────────────────────┐
│ 2. Host/model interprets it   │
│    and decides a search helps │
└───────────────┬───────────────┘
                ▼
┌───────────────────────────────┐
│ 3. MCP client requests the    │
│    server's available tools   │
│    using tools/list            │
└───────────────┬───────────────┘
                ▼
┌───────────────────────────────┐
│ 4. Host makes tool details    │
│    available to the model     │
└───────────────┬───────────────┘
                ▼
┌───────────────────────────────┐
│ 5. Model requests the tool    │
│    through host's tool flow   │
└───────────────┬───────────────┘
                ▼
┌───────────────────────────────┐
│ 6. Client sends tools/call    │
│    with name and arguments    │
└───────────────┬───────────────┘
                ▼
┌───────────────────────────────┐
│ 7. Server executes operation  │
│    and returns the result     │
└───────────────┬───────────────┘
                ▼
┌───────────────────────────────┐
│ 8. Host gives result to model │
│    to summarize               │
└───────────────┬───────────────┘
                ▼
┌───────────────────────────────┐
│ 9. User receives the answer   │
└───────────────────────────────┘
```

This illustrates the conceptual flow. In an actual implementation, initialization usually happens when the client establishes its MCP session, and tool discovery may be cached or repeated when needed.

## Example protocol messages

A simplified request to list tools:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/list"
}
```

A simplified tool-call request:

```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/call",
  "params": {
    "name": "search_lessons",
    "arguments": {
      "query": "checkpointing"
    }
  }
}
```

These messages illustrate the structure; they omit the initialization handshake and any additional fields required by the negotiated protocol version.

**Important distinction:** MCP communicates the tool request to the server. The model's decision to request the tool belongs to the host's AI workflow. MCP does not independently decide what the model should do.

---

# 7. Where LangGraph fits

You already know LangGraph's state, nodes, edges, conditional routing, `ToolNode`, and error handling. MCP adds a standardized way to access capabilities beyond your application.

## Responsibilities

| Technology | Main responsibility |
|---|---|
| LangGraph | Workflow orchestration: state, nodes, edges, loops, retries, checkpoints, and human approval |
| MCP | Protocol for discovering and interacting with server-provided capabilities |
| LangChain | Components such as chat models, prompts, tools, and integrations |
| Ollama | Runs supported models locally |

## A combined architecture

```text
                    USER
                      │
                      ▼
          ┌──────────────────────┐
          │    LangGraph Host    │
          │                      │
          │  State + Routing     │
          │  Assistant Node      │
          │  Error Handling      │
          └──────────┬───────────┘
                     │
                     ▼
          ┌──────────────────────┐
          │ Tool Adapter / Node  │
          │ Calls MCP client     │
          └──────────┬───────────┘
                     │
                MCP protocol
                     │
                     ▼
          ┌──────────────────────┐
          │     MCP Server       │
          │                      │
          │  Search / Read / API │
          └──────────┬───────────┘
                     │
                     ▼
              External system
```

This is a design pattern. MCP tools can be adapted into your LangGraph tool workflow, but you must implement or use a suitable integration. Not every MCP server is automatically a LangGraph node.

### A useful example

Suppose the agent must:

1. Search your repository through an MCP server.
2. Evaluate whether the results are relevant.
3. Search again if they are insufficient.
4. Ask for approval before modifying a file.
5. Return a summary.

MCP provides the repository capability interface. LangGraph coordinates the search, evaluation, retry loop, approval, and final response.

---

# 8. Local and remote servers

MCP servers can communicate over different transports.

## `stdio`

A local process communicates through standard input and output.

```text
Host / MCP client
       │
       │ stdin / stdout
       ▼
Local MCP server process
       │
       ▼
Local files or permitted services
```

This is convenient for local development. The client typically launches the server process and exchanges protocol messages over its standard streams. The server should not write unrelated logs to stdout if that would corrupt protocol communication.

## Streamable HTTP

A client communicates with an MCP server over HTTP using the Streamable HTTP transport.

```text
Host / MCP client
       │
       │ HTTP
       ▼
Remote or local MCP server
       │
       ▼
Database / API / other service
```

This is useful when the server runs as a service rather than as a child process launched by the client.

A remote server is not automatically safe merely because it uses HTTP. Authentication, authorization, transport security, origin validation, and deployment configuration matter.

We'll study transports and their exact behavior in Session 2 and the implementation sessions.

---

# 9. Security and practical boundaries

MCP makes integrations more standardized; it does not remove security responsibilities.

## Apply least privilege

Give a server access only to the files, database tables, or API operations it needs.

## Validate arguments

Do not trust tool arguments simply because they came from an LLM. Validate paths, types, ranges, and other constraints.

## Treat returned content as untrusted

A document or API response might contain misleading instructions. Tool output is data, not automatically an instruction the agent should follow.

## Protect side effects

Sending messages, modifying files, deleting records, or making purchases can have consequences. Add explicit approval and authorization where appropriate.

## Handle errors explicitly

Tool failures do not guarantee that the model will stop. Use structured error handling, retry limits, and graph routing for critical workflows.

## Keep secrets out of source control

Store credentials securely. Avoid printing tokens or sensitive information in logs.

> **Practical rule:** The model may propose an action, but the application and server must enforce what is actually allowed.

---

# 10. The mental model

Keep these distinctions clear:

- **Host:** the main AI application.
- **Client:** the component that speaks MCP to a server.
- **Server:** the provider of capabilities.
- **Tool:** an executable operation.
- **Resource:** data or context that can be read.
- **Prompt:** a reusable prompt template.
- **MCP:** the protocol that standardizes communication.
- **LangGraph:** the workflow orchestration layer that can use those capabilities.

### One-sentence summary

**MCP standardizes how AI applications discover and use external capabilities; LangGraph can orchestrate when and why an agent uses them.**

---

# 11. Quick revision

| Question | Short answer |
|---|---|
| What problem does MCP solve? | Fragmented, custom integrations between AI applications and external capabilities |
| What are the three architecture roles? | Host, Client, Server |
| What are the three core capability types? | Tools, Resources, Prompts |
| Which capability executes an operation? | Tool |
| Which capability exposes data to read? | Resource |
| Which capability provides reusable instructions? | Prompt |
| Is a REST API automatically an MCP server? | No; the server must implement the MCP protocol |
| Does MCP replace LangGraph? | No; they serve different roles |
| Must an MCP server be on a separate computer? | No; it can be a local process |
| Does MCP guarantee that a model chooses the right tool? | No; the host/model workflow handles that decision |
| What does `tools/list` do? | Lists available tools |
| What does `tools/call` do? | Requests execution of a tool |

---

# 12. Knowledge check

Try answering before checking the key.

### Q1. Architecture

Your application connects to a filesystem MCP server and a database MCP server. Which statement is accurate?

A. The host can manage separate clients for the two servers.  
B. Both servers must run inside the LangGraph graph.  
C. Each server must run on a separate physical computer.  
D. The client is the LLM itself.

### Q2. Capability types

You want to expose a reusable template that instructs a model to review Python code. Which capability best fits?

A. Resource  
B. Prompt  
C. Checkpointer  
D. Transport

### Q3. Protocol vs implementation

A Python function queries a database. You want compatible AI applications to discover and invoke it through MCP. What should you do?

A. Rename the function.  
B. Convert it to a LangGraph node only.  
C. Expose the operation through an MCP server that implements the protocol.  
D. Put the function's source code in a prompt.

### Q4. Request flow

What does the MCP client do when a tool is requested?

A. Trains the model on the tool's implementation.  
B. Communicates with the MCP server to request the operation.  
C. Automatically decides the user's intent without the host.  
D. Replaces the MCP server with a Python import.

### Q5. LangGraph and MCP

Which statement best describes their relationship?

A. MCP replaces graph state and conditional edges.  
B. LangGraph is a transport protocol for remote tools.  
C. MCP and LangGraph are competing model providers.  
D. LangGraph orchestrates workflow, while MCP standardizes communication with server-provided capabilities.

<details>
<summary><strong>Show answer key</strong></summary>

- Q1 — A
- Q2 — B
- Q3 — C
- Q4 — B
- Q5 — D

</details>

---

# 13. Mini challenge

Design a small MCP server for your learning repository.

It should expose these three capabilities:

| Type | Proposed name | Expected behavior |
|---|---|---|
| Tool | `search_lessons` | Search lesson files by keyword |
| Resource | `lesson://langgraph/core-concepts` | Provide the content of a selected lesson |
| Prompt | `quiz_from_lesson` | Create a reusable quiz-generation prompt |

Before writing code, answer these questions:

1. Which component would host your LangGraph agent?
2. Which component would communicate with the MCP server?
3. Which capability should execute a search?
4. Which capability should provide lesson content?
5. Which capability should provide quiz-generation instructions?

If you can explain the architecture and justify these three capability choices, you're ready to start building.

---

# 14. What's next?

**Session 2 — MCP protocol and lifecycle**

We'll learn:

1. JSON-RPC request and response structure.
2. How initialization works.
3. Capability negotiation.
4. Requests vs notifications.
5. Protocol errors and message flow.
6. How to inspect and debug an MCP interaction.

After that, we'll build a real Python MCP server, expose tools, resources, and prompts, and connect it to your LangGraph agent using your Windows + Python + Ollama environment.

## Official documentation

- [MCP introduction](https://modelcontextprotocol.io/introduction)
- [MCP architecture](https://modelcontextprotocol.io/docs/learn/architecture)
- [MCP server concepts](https://modelcontextprotocol.io/docs/learn/server-concepts)
- [MCP specification](https://modelcontextprotocol.io/specification/latest)

*This is a conceptual learning guide. Protocol and SDK details can evolve, so consult the current specification when implementing the examples.*
