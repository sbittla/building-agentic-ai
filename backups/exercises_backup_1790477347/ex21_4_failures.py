"""Exercise 21.4 (solution): a specialist that fails in three ways, each contained as an
ERROR result for the lead, plus one more chance after a contract violation."""
import ch21_orchestrator as orc

class RetryingTeam(orc.Team):
    """If a specialist broke the contract, ask once more with the reason in its brief."""
    def run_task(self, task):
        task = super().run_task(task)
        if task.status == "failed" and "(contract:" in (task.error or ""):
            reason = task.error.split("(contract:", 1)[1].rstrip(")")
            task.brief += (f"\n\nYour previous result was rejected by the contract:"
                           f"{reason}. Fix it and call submit_result again.")
            task.status, task.error = "open", None
            task = super().run_task(task)
        return task

def make_team(analyst_budget: int = 60_000, retry: bool = False) -> orc.Team:
    agents = list(orc.demo_team().agents.values())
    for a in agents:
        if a.name == "analyst":
            a.budget_tokens = analyst_budget
    return (RetryingTeam if retry else orc.Team)(agents, lead="lead")

def delegate_once(team: orc.Team, brief: str = "How many customers are there?") -> str:
    """What the lead's delegate call returns, without running the lead's model."""
    root = team.board.post("lead", "test goal", None, 0)
    return team.delegate(team.agents["lead"], "analyst", brief, root)

if __name__ == "__main__":
    print(delegate_once(make_team(analyst_budget=0)))
