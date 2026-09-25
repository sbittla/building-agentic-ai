"""Exercise 18.6 (solution): LangChain's human-in-the-loop middleware on add_task.

The middleware pauses the graph before add_task runs. A checkpointer stores the paused
state under a thread id; we resume it with the human's decision."""
import uuid
from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langchain_anthropic import ChatAnthropic
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command
from ch18_langchain import MODEL, add_task, list_tasks, today

def build(model=None):
    return create_agent(
        model=model or ChatAnthropic(model=MODEL),
        tools=[add_task, list_tasks, today],
        system_prompt="You manage the user's to-do list. Use the tools.",
        middleware=[HumanInTheLoopMiddleware(
            interrupt_on={"add_task": {"allowed_decisions": ["approve", "reject"]}})],
        checkpointer=InMemorySaver())             # needed to pause and resume

def ask_human(action) -> dict:
    yes = input(f"Allow {action['name']}({action['args']})? [y/N] ").strip().lower() == "y"
    return {"type": "approve"} if yes else {"type": "reject",
                                            "message": "The user declined to add this task."}

def ask(agent, question: str, decide=ask_human, thread_id=None):
    config = {"configurable": {"thread_id": thread_id or uuid.uuid4().hex}}
    state = agent.invoke({"messages": [{"role": "user", "content": question}]}, config)
    while state.get("__interrupt__"):                       # paused for approval
        request = state["__interrupt__"][0].value
        decisions = [decide(a) for a in request["action_requests"]]
        state = agent.invoke(Command(resume={"decisions": decisions}), config)
    return state["messages"][-1].content, state["messages"]

if __name__ == "__main__":
    agent = build()
    answer, _ = ask(agent, "Add 'renew passport' due 2026-11-01, then show my tasks.")
    print(answer)
