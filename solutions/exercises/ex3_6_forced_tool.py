"""Exercise 3.6 (solution): structured output two ways, with no JSON parsing either way."""
from sol_ch02_calculator_agent import client, MODEL

RECORD_CONTACT = {
    "name": "record_contact",
    "description": "Record a contact extracted from an email signature.",
    "input_schema": {"type": "object", "properties": {
        "name": {"type": "string"}, "email": {"type": ["string", "null"]},
        "company": {"type": ["string", "null"]}},
        "required": ["name", "email", "company"]}}

SIGNATURES = [
    "Best,\nPriya Raman\nStaff Engineer, Acme Corp\npriya.raman@acme.example",
    "--\nTom Becker | tom@becker-consulting.example | Becker Consulting",
    "Thanks! Ana (ana.li@example.org)",
    "Regards,\nDr. K. Okafor\nHead of Data, Nimbus Health\nk.okafor@nimbus.example",
    "Sent from my phone -- J. Smith, jsmith@example.net, Freelancer",
    "Cheers,\nSam Ortiz\nFabrikam Robotics",                     # no email address
]

def extract(signature: str) -> dict:
    r = client.messages.create(
        model=MODEL, max_tokens=2000, tools=[RECORD_CONTACT],
        tool_choice={"type": "tool", "name": "record_contact"},
        messages=[{"role": "user", "content": f"Extract the contact:\n{signature}"}])
    block = next(b for b in r.content if b.type == "tool_use")
    return block.input                    # already a dict: no json.loads needed

def extract_parsed(signature: str, client_=None):
    """The newer way: structured outputs. Returns a validated Contact object."""
    from ch03_structured import Contact
    c = client_ or client
    msg = c.messages.parse(model=MODEL, max_tokens=2000, output_format=Contact,
                           messages=[{"role": "user", "content": f"Extract the contact:\n{signature}"}])
    return msg.parsed_output

if __name__ == "__main__":
    for sig in SIGNATURES:
        print("forced tool:", extract(sig))
        print("parse():    ", extract_parsed(sig).model_dump())
    print("\nBoth avoid json.loads. parse() also validates the result into a typed object and "
          "works with extended thinking, where forcing a tool isn't allowed.")
