"""Exercise 21.6 (solution): a team with a remote member. The A2A analyst runs in this
process on its own port; the lead delegates to it and to the local analyst, compares
the answers, and sends a disagreement to the checker."""
import ch21_orchestrator as orc
from ch21_a2a_client import start_local_server

LEAD = ("You lead a small analytics team. Ask the SAME question to both analyst and "
        "remote_analyst. If their numbers differ, ask the checker. Finish with "
        "submit_result, naming the evidence you relied on.")

def mixed_team(url: str) -> orc.Team:
    base = orc.demo_team().agents
    lead = base["lead"]
    lead.system, lead.delegates_to = LEAD, ("analyst", "remote_analyst", "checker")
    remote = orc.Agent("remote_analyst", "the shop's data analyst, run by another team "
                       "and reached over A2A", system="", remote_url=url)
    return orc.Team([lead, base["analyst"], base["checker"], remote], lead="lead")

def main(question="How many orders were cancelled?", port=9997):
    url = start_local_server(port)
    team = mixed_team(url)
    out = team.run(question)
    print(out["board"])
    print(out["result"] or out["error"])
    print("tokens:", out["tokens"])
    return out

if __name__ == "__main__":
    main()
