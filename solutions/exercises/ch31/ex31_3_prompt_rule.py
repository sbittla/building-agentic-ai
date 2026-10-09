"""Exercise 31.3: a rule for what reaches the model.

check_design() asks WHERE a model runs. Ask WHAT it is sent too: personal data may
reach a model only inside the customer's own network ("customer-vpc") unless the field
is redacted first. Free: no model."""
from dataclasses import dataclass, field

from ch31_field import ENV, FIXED_DESIGN, Component, Environment, Violation, check_design

@dataclass
class ModelCall(Component):
    sends_fields: set = field(default_factory=set)   # fields that go into the prompt
    redacted: set = field(default_factory=set)       # fields masked before sending

def check_prompts(components: list[Component], env: Environment) -> list[Violation]:
    out = []
    for c in components:
        sent = getattr(c, "sends_fields", set()) - getattr(c, "redacted", set())
        leaked = sorted(sent & env.pii_fields)
        if c.model_host and c.model_host != "customer-vpc" and leaked:
            out.append(Violation("personal data to the model", c.name,
                                 f"sends {leaked} to a model on {c.model_host}",
                                 "redact them first, or run the model in customer-vpc"))
    return out

def check_all(components, env):
    return check_design(components, env) + check_prompts(components, env)

AGENT = ModelCall("agent service", "eu-central", holds_customer_data=True,
                  model_host="provider-eu", egress={"llm.eu.provider.example"},
                  logs_fields={"claim_id"}, retention_days=30, audit_log=True,
                  sends_fields={"claim_text", "name", "diagnosis", "policy_number"})
REDACTED = ModelCall(**{**AGENT.__dict__, "redacted": {"name", "policy_number"}})
IN_VPC = ModelCall(**{**AGENT.__dict__, "model_host": "customer-vpc"})

if __name__ == "__main__":
    others = [c for c in FIXED_DESIGN if c.name != "agent service"]
    for label, agent in (("unredacted", AGENT), ("names redacted", REDACTED),
                         ("model in their VPC", IN_VPC)):
        found = check_all(others + [agent], ENV)
        print(f"{label}:", [f"{v.component}: {v.detail}" for v in found] or "no violations")
    assert check_all(others + [AGENT], ENV)
    assert check_all(others + [REDACTED], ENV)          # diagnosis still goes out
    assert not check_all(others + [IN_VPC], ENV)
