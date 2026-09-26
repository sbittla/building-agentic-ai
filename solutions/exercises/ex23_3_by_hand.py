"""Exercise 23.3 (solution): drive the browser harness by hand, with no model. The same
calls the agent makes, so you can see what each one returns."""
import ch23_backoffice as app
from ch23_browser import Browser

def main(port: int = 8769):
    app.reset()
    b = Browser(app.serve(port), approver=lambda action: False)
    try:
        b.sign_in("agent-bot", app.USERS["agent-bot"])
        print(b.open("/customers?q=chen"))
        print(b.click("e3"))                            # the link to Chen Wei
        b.type_text("e1", "1 Marina Way, Singapore")
        print(b.click("e2"))                            # Save address
        b.type_text("e3", "20")
        print(b.click("e5"))                            # Issue credit: refused
        print(b.open("https://example.com"))            # refused by the allowlist
        print("\n".join(f"{t} {what}" for t, what in b.log))
    finally:
        b.close()
    return app.CUSTOMERS[3]

if __name__ == "__main__":
    print(main())
