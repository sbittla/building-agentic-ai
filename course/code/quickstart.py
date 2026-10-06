"""Your first agent, free: no API key, no download, nothing to pay.

    ./course.sh quickstart

This runs the real agent loop from Chapter 4 (run_agent) with the real date tools from
Chapter 3. Only the model is replaced: a scripted stand-in plays the part a real model
plays, asking for one tool, reading the result and asking for the next. So you see
exactly what an agent run looks like, step by step, before you set up a model.
"""
import re
from datetime import date
from types import SimpleNamespace as NS

import ch04_agent
from ch03_tools import TOOLS, run_tool

QUESTION = "How many days until July 4 next, and what weekday will it be?"


class ScriptedModel:
    """Stands in for the Claude API. A real model chooses these steps itself."""
    def __init__(self):
        self.messages = self
        self.step = 0

    def create(self, model, messages, tools=None, **kwargs):
        self.step += 1
        last = messages[-1]["content"]
        result = last[0]["content"] if isinstance(last, list) else ""
        if self.step == 1:                                   # "I need today's date"
            content = [NS(type="tool_use", id="toolu_1", name="get_current_date", input={})]
        elif self.step == 2:                                 # "now count the days"
            today = date.fromisoformat(re.match(r"\d{4}-\d\d-\d\d", result).group())
            july4 = date(today.year, 7, 4)
            if july4 <= today:
                july4 = date(today.year + 1, 7, 4)
            content = [NS(type="tool_use", id="toolu_2", name="days_between",
                          input={"start": today.isoformat(), "end": july4.isoformat()})]
        else:                                                # "I have what I need"
            days, rest = result.split(" days; ")
            content = [NS(type="text", text=f"It's {days} days until July 4; {rest.rstrip('.')}.")]
        stop = "tool_use" if content[0].type == "tool_use" else "end_turn"
        return NS(content=content, stop_reason=stop, stop_details=None,
                  usage=NS(input_tokens=0, output_tokens=0))


if __name__ == "__main__":
    print(f"Question: {QUESTION}\n")
    print("The agent loop runs (each line is one tool the model asked for):\n")
    ch04_agent._client = ScriptedModel()                   # the only thing that's not real
    answer, messages, stats = ch04_agent.run_agent(QUESTION, TOOLS, run_tool)
    print(f"\nANSWER: {answer}")
    print(f"\nThat was {stats['steps']} model calls and {stats['tool_calls']} tool calls: the model "
          "asked, your code ran the tool, the result went back, and the loop repeated until the "
          "model answered. Chapter 4 builds this loop.")
    print("""
This run used a scripted stand-in model, so it was free and needed no key. To see a real
model make these choices itself, pick one (section "Choose your model" in the book):

  Free, on your computer:  ./course.sh local up     (downloads about 6.6 GB, once)
                           then set PROVIDER=local in .env
  Claude:                  ./course.sh setup        (paste your API key)

Then run:  ./course.sh python ch04_agent.py""")
