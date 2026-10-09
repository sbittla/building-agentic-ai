"""Exercise 31.4: how many more pilot runs?

At week 2 the pilot passed 37 of 40 runs: 92.5%, but the 95% interval's lower bound
(80%) doesn't clear the signed 85%. If the true rate is what we've seen so far, how
many runs does the pilot need before the gate can promote? Free: arithmetic."""
from ch27_eval import wilson
from ch31_field import Criteria

def runs_needed(passes: int, runs: int, min_success: float = Criteria().min_success,
                limit: int = 10_000) -> int | None:
    """The smallest total number of runs at the observed rate whose lower bound clears
    min_success. None if even `limit` runs wouldn't (the rate itself is too low)."""
    rate = passes / runs
    if rate <= min_success:
        return None
    for n in range(runs, limit + 1):
        if wilson(round(rate * n), n)[0] >= min_success:
            return n
    return None

if __name__ == "__main__":
    for p, n in ((37, 40), (45, 50), (88, 100), (42, 50)):
        need = runs_needed(p, n)
        print(f"{p}/{n} ({p / n:.1%}): " +
              (f"about {need} runs in total, {need - n} more" if need else
               "no number of runs will do: fix the agent first"))
    assert runs_needed(37, 40) > 40 and runs_needed(42, 50) is None
