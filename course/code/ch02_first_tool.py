"""Chapter 2: your first tool. The model can't know today's date; this tool tells it."""
import os
from datetime import date
from anthropic import Anthropic

MODEL = os.environ.get("MODEL", "claude-sonnet-5")
client = Anthropic()

def get_today() -> str:                              # 1. an ordinary Python function
    return date.today().strftime("%A, %d %B %Y")

TOOLS = [{                                           # 2. its description, for the model
    "name": "get_today",
    "description": "Today's date and weekday. Use it for any question about today, "
                   "the current date, or how far away a date is.",
    "input_schema": {"type": "object", "properties": {}},     # no arguments needed
}]

question = "What's the date today, and what day of the week is it?"
messages = [{"role": "user", "content": question}]

reply = client.messages.create(model=MODEL, max_tokens=2000, tools=TOOLS, messages=messages)
print("stop_reason:", reply.stop_reason)             # "tool_use": the model ASKS for the tool

tool_call = next(b for b in reply.content if b.type == "tool_use")
print("the model asked for:", tool_call.name, tool_call.input)
result = get_today()                                 # 3. YOUR code runs it
print("our code answered:", result)

messages.append({"role": "assistant", "content": reply.content})           # what it asked
messages.append({"role": "user", "content": [                              # what we found
    {"type": "tool_result", "tool_use_id": tool_call.id, "content": result}]})

final = client.messages.create(model=MODEL, max_tokens=2000, tools=TOOLS, messages=messages)
print("\nANSWER:", "".join(b.text for b in final.content if b.type == "text"))            # 4. the model answers with the result
