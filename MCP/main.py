import random
from fastmcp import FastMCP

mcp = FastMCP(
    name="Demo-Mcp-Server",
    version="v0.0.1"
)

@mcp.tool
def roll_dice(n_dice:int=1) -> list[int]:
    '''Roll n_dice and return the result'''
    return [random.randint(1,6) for _ in range(n_dice)]

@mcp.tool
def add_num(a:float, b:float) -> float:
    '''Add two number together'''
    return a+b

@mcp.tool
def greet(name: str) -> str:
    return f"Hello, {name}!"

if __name__ == "__main__":
    mcp.run()