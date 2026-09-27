"""Exercise 2.3 (Simple): print the raw tool_use block from the first model call."""
import ch02_calculator_agent as c2

def first_response(question: str):
    r = c2.client.messages.create(model=c2.MODEL, max_tokens=2000, tools=c2.TOOLS,
                                  messages=[{"role": "user", "content": question}])
    for block in r.content:
        print(" ", block)
    return r

if __name__ == "__main__":
    for q in ["What is 17.5% of 84,213?", "What is 2**20 - 1?", "What is 3 + 4 * 5?"]:
        print(f"\n{q}  stop_reason:", first_response(q).stop_reason)
