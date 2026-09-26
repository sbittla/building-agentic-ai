"""Chapter 3: getting JSON you can rely on. Two API features do the work:

1. Structured outputs: the model's REPLY must match a schema. messages.parse() takes a
   Pydantic class and gives you back an object of that class.
2. Strict tools: "strict": True makes the model's tool INPUT match the tool's schema
   exactly, so run_tool never sees a missing field or a wrong type."""
import os
from anthropic import Anthropic
from pydantic import BaseModel

MODEL = os.environ.get("MODEL", "claude-sonnet-5")
client = Anthropic()

# ---- 1. Structured outputs: describe the answer's shape as a class -----------------
class Contact(BaseModel):
    name: str
    email: str | None
    company: str | None

def extract_contact(signature: str) -> Contact:
    msg = client.messages.parse(
        model=MODEL, max_tokens=2000, output_format=Contact,
        messages=[{"role": "user",
                   "content": f"Extract the contact details:\n{signature}"}])
    return msg.parsed_output                   # a Contact object, already validated

# The same thing without Pydantic: pass the JSON Schema yourself and parse the text.
RAW_REQUEST = {"output_config": {"format": {"type": "json_schema",
                                            "schema": Contact.model_json_schema()}}}

# ---- 2. Strict tools: the input ALWAYS matches the schema --------------------------
STRICT_CONVERT = {
    "name": "convert_units",
    "description": "Convert a value between km, mi, m (length) or kg, lb, g (mass).",
    "strict": True,                            # inputs are guaranteed to fit the schema
    "input_schema": {
        "type": "object",
        "properties": {"value": {"type": "number"},
                       "from_unit": {"type": "string",
                                     "enum": ["km", "mi", "m", "kg", "lb", "g"]},
                       "to_unit": {"type": "string",
                                   "enum": ["km", "mi", "m", "kg", "lb", "g"]}},
        "required": ["value", "from_unit", "to_unit"],
        "additionalProperties": False,         # strict schemas must say this
    },
}

if __name__ == "__main__":
    c = extract_contact("Best,\nPriya Nair | Head of Ops, Northwind Ltd | "
                        "priya@northwind.example")
    print(c)                                   # name='Priya Nair' email=... company=...
    print(c.model_dump())
