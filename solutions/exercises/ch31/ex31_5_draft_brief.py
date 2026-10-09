"""Exercise 31.5: let the model draft the brief, and let code decide.

Give draft_brief() your own interview notes (or the sample ones), print what
check_brief() still finds missing and the questions to ask next, then fill in the
answers you got and check again. Uses the model for the draft."""
import sys
from dataclasses import replace

from ch31_field import NOTES, Metric, check_brief, draft_brief

def answers_from_followup(brief):
    """What the follow-up call established (edit these for your own engagement)."""
    return replace(brief,
                   metric=Metric("minutes to summarize a claim file", "minutes", 18, 9,
                                 "time study of 40 claims over two weeks in March"),
                   customer_owner=brief.customer_owner or "Anna Weber, head of claims operations",
                   non_goals=brief.non_goals or ["deciding claims", "writing to customers"])

if __name__ == "__main__":
    notes = open(sys.argv[1]).read() if len(sys.argv) > 1 else NOTES
    brief, questions = draft_brief(notes, "Lakeside Insurance")
    print("Draft problems:", *check_brief(brief), sep="\n  - ")
    print("Ask next:", *questions, sep="\n  - ")
    final = answers_from_followup(brief)
    print("\nAfter the follow-up:", check_brief(final) or "ready to build")
