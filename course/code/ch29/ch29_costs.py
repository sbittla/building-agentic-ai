"""Chapter 29: cost and capacity engineering. Where an agent's money and time go, what
the levers do, and budgets that are enforced in code rather than hoped for.

  * estimate   the cost of a run, step by step, with and without prompt caching
  * budgets    a per-request cap (inside the loop) and a per-user daily cap
  * capacity   how many requests you can serve, from latency and rate limits

    ./course.sh python ch29_costs.py        a cost breakdown and a capacity plan"""
import time
from dataclasses import dataclass, field

from ch20_router import PRICES, cost

CACHE_WRITE, CACHE_READ = 1.25, 0.10     # multiples of the input price (Chapter 16)

# ------------------------------------------------------------ 1. where the money goes
def estimate(steps: int, prefix: int, question: int, per_step_in: int,
             per_step_out: int, model: str = "claude-sonnet-5",
             cache: bool = False) -> dict:
    """A run of `steps` model calls. Each call resends the prefix (system prompt and
    tools), the question and everything added so far. That growing history is why
    agents cost more than their prompts suggest."""
    price_in, price_out = PRICES[model]
    total_in = total_out = dollars = 0.0
    history = question
    for step in range(steps):
        if cache:                             # the prefix is written once, then read
            rate = CACHE_WRITE if step == 0 else CACHE_READ
            dollars += prefix * price_in * rate / 1e6
            dollars += history * price_in / 1e6
        else:
            dollars += (prefix + history) * price_in / 1e6
        dollars += per_step_out * price_out / 1e6
        total_in += prefix + history
        total_out += per_step_out
        history += per_step_out + per_step_in  # the reply and the tool result stay
    return {"input_tokens": int(total_in), "output_tokens": int(total_out),
            "dollars": round(dollars, 5)}

# ------------------------------------------------------------ 2. budgets in code
def request_budget(dollars: float, model: str | None = None):
    """A should_stop hook for run_agent: stop the loop before a run overspends."""
    def should_stop(stats: dict) -> str | None:
        spent = cost({**stats, "model": model or stats.get("model")})
        return f"request budget of ${dollars:.2f} reached" if spent >= dollars else None
    return should_stop

@dataclass
class DailyBudget:
    """A per-user daily cap, checked before a run starts and charged after it ends."""
    limit: float
    spent: dict = field(default_factory=dict)          # (user, day) -> dollars

    def _key(self, user):
        return (user, time.strftime("%Y-%m-%d"))

    def allow(self, user: str) -> bool:
        return self.spent.get(self._key(user), 0.0) < self.limit

    def charge(self, user: str, stats: dict) -> float:
        key = self._key(user)
        self.spent[key] = self.spent.get(key, 0.0) + cost(stats)
        return self.spent[key]

# ------------------------------------------------------------ 3. capacity
def concurrency_needed(arrivals_per_s: float, latency_s: float) -> float:
    """Little's law: requests in flight = arrival rate x time each one takes."""
    return arrivals_per_s * latency_s

def rate_limited_capacity(rpm: int, tpm: int, calls_per_request: float,
                          tokens_per_request: float) -> float:
    """Requests per minute the provider's limits allow: the tighter of the two."""
    return min(rpm / calls_per_request, tpm / tokens_per_request)

if __name__ == "__main__":
    base = dict(steps=6, prefix=6_000, question=100, per_step_in=800, per_step_out=300)
    plain, cached = estimate(**base), estimate(**base, cache=True)
    small = estimate(**base, model="claude-haiku-4-5", cache=True)
    print(f"6-step run, Sonnet: ${plain['dollars']:.4f}; with caching "
          f"${cached['dollars']:.4f}; Haiku with caching ${small['dollars']:.4f}")
    print(f"  input tokens sent: {plain['input_tokens']:,} "
          f"(the prefix alone is {6 * 6_000:,})")
    print(f"10 requests/s at 8 s each needs {concurrency_needed(10, 8):.0f} in flight")
    print(f"Limits of 4,000 requests and 2,000,000 tokens a minute allow "
          f"{rate_limited_capacity(4_000, 2_000_000, 6, 60_000):.0f} runs a minute")
