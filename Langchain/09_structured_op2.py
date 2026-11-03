from pydantic import BaseModel, Field
from typing import Literal

from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
from utils import getmodel


class TopicAnalysis(BaseModel):
    topic: str
    difficulty: Literal[
        "beginner",
        "intermediate",
        "advanced"
    ]
    key_concepts: list[str] = Field(
        max_length=10,
        description="At most 10 distinct concepts"
    )
    estimated_study_minutes: int = Field(gt=0)


prompt = ChatPromptTemplate.from_template("""
Analyze this computer science topic: {topic}

Return a concise result containing:
- topic
- difficulty
- key_concepts: 3 to 5 distinct concepts
- estimated_study_minutes: a positive integer

Do not repeat concepts. Complete every required field.
""")

llm = ChatOllama(
    model=getmodel(),
    temperature=0,
    num_predict=256
)

structured_llm = llm.with_structured_output(
    TopicAnalysis,
    method="json_schema",
    include_raw=True
)

result = (prompt | structured_llm).invoke({
    "topic": "process scheduling"
})

print("RAW RESPONSE:")
print(result["raw"].content)

print("\nPARSED RESULT:")
print(result["parsed"])

print("\nPARSING ERROR:")
print(result["parsing_error"])