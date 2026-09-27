"""Exercise 26.4 (solution): the Chapter 21 team with tokens. The lead's token is
attenuated for each specialist: fewer scopes, a shorter life, a record of where it
came from. Tools check the token; agents never see it."""
import ch21_orchestrator as orc
import ch26_identity as ident

ident.AGENTS.setdefault("lead-agent", {"orders:read", "refunds:create"})
ident.AGENTS.setdefault("checker-agent", {"orders:read"})
SPECIALIST = {"analyst": ("analyst-agent", {"orders:read"}),
              "checker": ("checker-agent", {"orders:read"})}

ORDER_TOOL = {"name": "get_order", "description": "Look up an order of the user you "
              "work for.", "input_schema": {"type": "object", "required": ["order_id"],
                                            "properties": {"order_id": {"type": "string"}}}}

class TokenTeam(orc.Team):
    def __init__(self, agents, lead, lead_token):
        super().__init__(agents, lead)
        self.tokens = {}                        # task id -> token, held by the harness
        self.lead_token = lead_token

    def run_task(self, task):
        token = self.tokens.setdefault(task.id, self.lead_token)
        agent = self.agents[task.agent]
        agent.tools = [ORDER_TOOL]
        agent.run_tool = lambda name, args: self._order_tool(token, name, args)
        return super().run_task(task)

    @staticmethod
    def _order_tool(token, name, args):
        try:
            return ident.get_order(token, **args)
        except ident.Denied as exc:
            return f"ERROR: not authorized: {exc}"

    def delegate(self, caller, name, brief, parent):
        """Chapter 21's delegate, plus a narrower token for the specialist."""
        if name not in caller.delegates_to:
            return f"ERROR: {caller.name} may not delegate to {name}"
        agent_id, scopes = SPECIALIST[name]
        parent_token = self.tokens.get(parent.id, self.lead_token)
        try:
            child = ident.attenuate(parent_token, ident.API, scopes, agent=agent_id,
                                    ttl=300)
        except ident.Denied as exc:
            return f"ERROR: {exc}"
        task = self.board.post(name, brief, parent.id, parent.depth + 1)
        if isinstance(task, str):
            return f"ERROR: {task}"
        if task.status == "open":
            self.tokens[task.id] = child
            task = self.run_task(task)
        if task.status != "done":
            return f"ERROR: {name} failed: {task.error}"
        return (f'<result from="{name}" task="{task.id}">\n'
                f"{orc.json.dumps(task.result, indent=1)}\n</result>")

def make_team(user: str = "ana") -> TokenTeam:
    lead_token = ident.mint("lead-agent", user, {"orders:read", "refunds:create"},
                            ident.API, ttl=900)
    return TokenTeam(list(orc.demo_team().agents.values()), "lead", lead_token)

if __name__ == "__main__":
    team = make_team()
    print(team.run("What did Ana pay for order A-1002? Have it checked.")["board"])
