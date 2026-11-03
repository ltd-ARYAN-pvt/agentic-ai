from langchain_core.tools import tool


@tool
def multiply(a: int, b: int) -> int:
    """Multiply two integers and return the result."""
    return a * b


print("Tool name:", multiply.name)
print("Tool description:", multiply.description)
print("Direct execution:", multiply.invoke({"a": 18742, "b": 9361}))