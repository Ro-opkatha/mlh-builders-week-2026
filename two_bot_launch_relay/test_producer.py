
from pathlib import Path

from crewai import Agent, Task, Crew, Process, LLM

BASE_DIR = Path(__file__).resolve().parent
BRIEF_PATH = BASE_DIR / "launch-desk" / "source-brief.md"

llm = LLM(
    model="ollama_chat/qwen3.5:2b",
    base_url="http://localhost:11434",
    temperature=0.2,
    max_tokens=1024,
    reasoning_effort="none",
)

agent = Agent(
    role="Launch Producer",
    goal="Create accurate and engaging launch announcements.",
    backstory=(
        "You are a careful communications specialist. "
        "Use only verified information from the approved source brief."
    ),
    llm=llm,
    verbose=True,
)

task = Task(
    description=f"""
    Read this approved source brief:

    {BRIEF_PATH.read_text(encoding="utf-8")}

    Create a short test announcement of approximately 60 words
    for students and young professionals in Kolkata.

    Do not invent event names, dates, venues, prices, or availability.
    Return only the announcement text.
    """,
    expected_output="A factual announcement of approximately 60 words.",
    agent=agent,
)

crew = Crew(
    agents=[agent],
    tasks=[task],
    process=Process.sequential,
    verbose=True,
)

result = crew.kickoff()

print("\n========== PRODUCER TEST RESULT ==========\n")
print(result)
