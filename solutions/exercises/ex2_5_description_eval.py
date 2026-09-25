"""Exercise 2.5 (Medium): measure whether the description makes the model call the tool."""
import copy
import ch02_calculator_agent as c2

QUESTIONS = [  # (question, should_call_tool)
    ("What is 17.5% of 84,213?", True), ("What is 1234 * 5678?", True),
    ("Divide 1,000,000 by 7.", True), ("What is 2 to the power 31?", True),
    ("What's 15% tip on $86.40?", True), ("Add 19.99, 5.49 and 3.75.", True),
    ("What is 999999 squared?", True),
    ("What is a prime number?", False), ("Who invented the calculator?", False),
    ("Explain what a percentage is.", False),
]
WEAK = "Calculator."

def tool_rate(description: str):
    tools = copy.deepcopy(c2.TOOLS)
    tools[0]["description"] = description
    rows = []
    for q, should in QUESTIONS:
        r = c2.client.messages.create(model=c2.MODEL, max_tokens=2000, tools=tools,
                                      messages=[{"role": "user", "content": q}])
        called = any(b.type == "tool_use" for b in r.content)
        rows.append((q, should, called))
    correct = sum(called == should for _, should, called in rows)
    return correct, rows

def main():
    report = {}
    for label, desc in [("weak", WEAK), ("strong", c2.TOOLS[0]["description"])]:
        correct, rows = tool_rate(desc)
        report[label] = correct
        print(f"\n{label} description: {correct}/{len(rows)} correct")
        for q, should, called in rows:
            if called != should:
                print(f"   MISS  should_call={should} called={called}  {q}")
    return report

if __name__ == "__main__":
    main()
