"""Chapter 24 (3/3): LangChain's create_agent (built on LangGraph). Model-agnostic:
swap ChatAnthropic for another provider's chat model and the agent stays the same."""
import os
from langchain.agents import create_agent
from langchain_anthropic import ChatAnthropic
import ch05_todo_tools as todo

MODEL = os.environ.get("MODEL", "claude-sonnet-5")

# Plain Python functions become tools: the docstring is the description,
# the type hints are the schema. (Exactly what you did by hand in chapter 2.)
def add_task(title: str, due: str | None = None) -> str:
    """Add a to-do. due is YYYY-MM-DD."""
    return todo.add_task(title, due)

def list_tasks(due_before: str | None = None) -> str:
    """List open tasks, optionally only those due on or before a date."""
    return todo.list_tasks(due_before=due_before)

def today() -> str:
    """Today's date, YYYY-MM-DD."""
    return todo.today()

def build(model=None):
    return create_agent(model=model or ChatAnthropic(model=MODEL),
                        tools=[add_task, list_tasks, today],
                        system_prompt="You manage the user's to-do list. Use the tools.")

def ask(agent, question: str, history=None):
    state = agent.invoke({"messages": (history or []) + [{"role": "user", "content": question}]})
    return state["messages"][-1].content, state["messages"]

if __name__ == "__main__":
    agent = build()
    answer, history = ask(agent, "Add 'renew passport' due 2026-11-01, then show my tasks.")
    print(answer)
