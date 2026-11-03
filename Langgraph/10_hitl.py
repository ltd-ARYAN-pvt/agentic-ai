from typing import TypedDict, Literal
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import interrupt, Command


class EmailState(TypedDict):
    recipient: str
    email_body: str
    approved: bool
    status: str


def draft_email(state: EmailState):
    return {
        "email_body": (
            f"Dear {state['recipient']},\n"
            "I hope you are doing well.\n"
            "Best regards"
        )
    }


def request_approval(state: EmailState):
    decision = interrupt({
        "question": "Do you approve this email?",
        "recipient": state["recipient"],
        "email_body": state["email_body"],
        "options": ["approve", "reject"]
    })

    if decision not in ("approve", "reject"):
        raise ValueError("Invalid approval decision")

    return {"approved": decision == "approve"}


def route_decision(
    state: EmailState,
) -> Literal["send", "reject"]:
    if state["approved"]:
        return "send"
    return "reject"


def send_email(state: EmailState):
    # Simulation only: no real email is sent.
    print("SIMULATED: Email approved for sending.")
    return {"status": "Approved"}


def reject_email(state: EmailState):
    print("Email rejected.")
    return {"status": "Rejected"}


builder = StateGraph(EmailState)

builder.add_node("draft", draft_email)
builder.add_node("approval", request_approval)
builder.add_node("send", send_email)
builder.add_node("reject", reject_email)

builder.add_edge(START, "draft")
builder.add_edge("draft", "approval")

builder.add_conditional_edges(
    "approval",
    route_decision,
    {
        "send": "send",
        "reject": "reject"
    }
)

builder.add_edge("send", END)
builder.add_edge("reject", END)

graph = builder.compile(checkpointer=InMemorySaver())

config = {
    "configurable": {"thread_id": "email-001"}
}

# Step 1: Run until the graph pauses for approval.
result = graph.invoke(
    {
        "recipient": "Professor",
        "email_body": "",
        "approved": False,
        "status": ""
    },
    config=config
)

print("Paused:", result["__interrupt__"])

# Step 2: Resume after reviewing the interrupt.
decision = input("Enter approve or reject: ").strip().lower()

if decision in ("approve", "reject"):
    result = graph.invoke(
        Command(resume=decision),
        config=config
    )
    print("Final state:", result)
else:
    print("Invalid decision. The graph remains paused.")