"""Chapter 21: orchestrating a team of agents. A lead delegates tasks to specialists
through one tool; code enforces everything the team must not get wrong:

  * contracts   every result must match a JSON schema, checked in code
  * a board     one shared record of who is doing what, and what came back
  * limits      delegation depth, number of tasks, and a token budget per agent
  * dedupe      the same task for the same agent isn't done twice
  * isolation   each specialist gets a brief, never the lead's whole conversation
  * containment a failed specialist returns an error the lead can handle

A specialist can also be a REMOTE agent reached over A2A (section 21.7).

    ./course.sh python ch21_orchestrator.py
    ./course.sh python ch21_orchestrator.py "Which city should get our next promotion?"
"""
import json
import sys
import threading
from dataclasses import dataclass, field

import jsonschema

import ch08_sql_tools as sql
from ch04_agent import run_agent

# ------------------------------------------------------------ 1. the contract
RESULT = {"type": "object", "additionalProperties": False,
          "required": ["answer", "evidence", "confidence"],
          "properties": {
              "answer": {"type": "string", "maxLength": 2000},
              "evidence": {"type": "array", "items": {"type": "string"}, "maxItems": 8},
              "confidence": {"type": "string", "enum": ["low", "medium", "high"]}}}

SUBMIT = {"name": "submit_result", "input_schema": RESULT,
          "description": "Hand your finished result to whoever gave you the task. "
                         "Call it exactly once, at the end. Evidence: the queries, "
                         "files or sources behind the answer."}

# ------------------------------------------------------------ 2. agents and the board
@dataclass
class Agent:
    name: str
    role: str                          # one line the lead reads to choose a delegate
    system: str
    tools: list = field(default_factory=list)
    run_tool: object = None
    delegates_to: tuple = ()           # which agents this one may hand work to
    budget_tokens: int = 60_000
    remote_url: str | None = None      # an A2A agent (section 21.7)
    spent: int = 0

@dataclass
class Task:
    id: int
    agent: str
    brief: str
    parent: int | None
    depth: int
    status: str = "open"               # open -> done | failed | refused
    result: dict | None = None
    error: str | None = None

class Board:
    """The shared record of the team's work (a "blackboard"). Everyone can read it;
    only the orchestrator code writes it."""
    def __init__(self, max_tasks=10, max_depth=2):
        self.tasks: list[Task] = []
        self.max_tasks, self.max_depth = max_tasks, max_depth
        self.lock = threading.Lock()

    def post(self, agent, brief, parent, depth) -> Task | str:
        key = (agent, " ".join(brief.lower().split()))
        with self.lock:
            for t in self.tasks:                          # the same task twice?
                if (t.agent, " ".join(t.brief.lower().split())) == key \
                        and t.status == "done":
                    return t
            if depth > self.max_depth:
                return f"refused: delegation deeper than {self.max_depth} levels"
            if len(self.tasks) >= self.max_tasks:
                return f"refused: the team's limit of {self.max_tasks} tasks is reached"
            task = Task(len(self.tasks) + 1, agent, brief, parent, depth)
            self.tasks.append(task)
            return task

    def show(self) -> str:
        return "\n".join(f"#{t.id} {'  ' * t.depth}{t.agent:<10} {t.status:<8} "
                         f"{t.brief[:60]}" for t in self.tasks)

# ------------------------------------------------------------ 3. the orchestrator
class Team:
    def __init__(self, agents: list[Agent], lead: str, board: Board | None = None):
        self.agents = {a.name: a for a in agents}
        self.lead, self.board = lead, board or Board()

    def delegate_tool(self, caller: Agent) -> dict:
        names = list(caller.delegates_to)
        roles = "; ".join(f"{n}: {self.agents[n].role}" for n in names)
        return {"name": "delegate", "description": f"Give one self-contained task to "
                f"a specialist and get their result. Specialists: {roles}. Write a "
                f"complete brief: they can't see this conversation.",
                "input_schema": {"type": "object", "required": ["agent", "brief"],
                                 "properties": {"agent": {"type": "string",
                                                          "enum": names},
                                                "brief": {"type": "string"}}}}

    def run_task(self, task: Task) -> Task:
        agent = self.agents[task.agent]
        if agent.spent >= agent.budget_tokens:
            task.status, task.error = "failed", f"{agent.name} is over its token budget"
            return task
        if agent.remote_url:
            return self._run_remote(agent, task)
        submitted, violations = {}, []
        tools = list(agent.tools) + [SUBMIT]
        if agent.delegates_to and task.depth < self.board.max_depth:
            tools.append(self.delegate_tool(agent))

        def run_tool(name, args):
            if name == "submit_result":
                try:
                    jsonschema.validate(args, RESULT)          # the contract, in code
                except jsonschema.ValidationError as exc:
                    violations.append(exc.message)
                    return f"ERROR: result doesn't match the contract: {exc.message}"
                submitted.update(args)
                return "Result received. Stop here."
            if name == "delegate":
                return self.delegate(agent, args["agent"], args["brief"], task)
            return agent.run_tool(name, args)

        _, _, stats = run_agent(task.brief, tools, run_tool, system=agent.system,
                                verbose=False, max_iterations=10)
        agent.spent += stats["input_tokens"] + stats["output_tokens"]
        if submitted:
            task.status, task.result = "done", submitted
        else:
            task.status = "failed"
            task.error = f"{agent.name} ended without submitting a valid result"
            if violations:
                task.error += f" (contract: {violations[-1]})"
        return task

    def delegate(self, caller: Agent, name: str, brief: str, parent: Task) -> str:
        if name not in caller.delegates_to:
            return f"ERROR: {caller.name} may not delegate to {name}"
        task = self.board.post(name, brief, parent.id, parent.depth + 1)
        if isinstance(task, str):
            return f"ERROR: {task}"
        if task.status == "open":
            task = self.run_task(task)
        if task.status != "done":
            return f"ERROR: {name} failed: {task.error}"        # contained, not raised
        # A specialist's answer is data from another model, labelled as such.
        return (f'<result from="{name}" task="{task.id}">\n'
                f"{json.dumps(task.result, indent=1)}\n</result>")

    def _run_remote(self, agent: Agent, task: Task) -> Task:
        import asyncio
        from ch21_a2a_client import ask_remote_agent
        try:
            text = asyncio.run(ask_remote_agent(agent.remote_url, task.brief,
                                                show=False))
            task.status = "done"
            task.result = {"answer": text[:2000], "evidence": [agent.remote_url],
                           "confidence": "medium"}
        except Exception as exc:
            task.status, task.error = "failed", f"{type(exc).__name__}: {exc}"
        return task

    def run(self, goal: str) -> dict:
        root = self.board.post(self.lead, goal, None, 0)
        self.run_task(root)
        return {"status": root.status, "result": root.result, "error": root.error,
                "board": self.board.show(),
                "tokens": {a.name: a.spent for a in self.agents.values()}}

# ------------------------------------------------------------ 4. a demo team
def demo_team() -> Team:
    rules = (" Finish by calling submit_result with your answer, evidence and "
             "confidence.")
    return Team([
        Agent("lead", "plans the work and writes the final recommendation",
              "You lead a small analytics team. Split the goal into tasks, delegate "
              "each with a complete brief, compare what comes back, and resolve "
              "disagreements by asking the checker." + rules,
              delegates_to=("analyst", "checker")),
        Agent("analyst", "answers questions about the shop's sales data with SQL",
              sql.SYSTEM + rules, sql.TOOLS, sql.run_tool),
        Agent("checker", "independently re-checks a claimed number with its own SQL",
              "You verify claims. Write your own query; don't trust the claim's SQL. "
              "Say clearly whether the claim holds." + rules, sql.TOOLS, sql.run_tool),
    ], lead="lead")

if __name__ == "__main__":
    goal = " ".join(sys.argv[1:]) or ("Which city should get our next promotion? Base "
                                      "it on revenue, and have the key number checked.")
    out = demo_team().run(goal)
    print(out["board"], "\n")
    print(json.dumps(out["result"], indent=1) if out["result"] else out["error"])
    print("tokens:", out["tokens"])
