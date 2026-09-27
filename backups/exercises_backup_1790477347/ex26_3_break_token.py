"""Exercise 26.3 (solution): five ways to misuse a token, and one way to over-ask."""
import time

import ch26_identity as ident

def attempt(label, fn):
    try:
        fn()
        return (label, "ACCEPTED")
    except ident.Denied as exc:
        return (label, str(exc))

def main():
    good = ident.mint("support-agent", "ana", {"orders:read"}, ident.API)
    tampered = good[:-2] + ("A" if good[-2] != "A" else "B") + good[-1]
    short = ident.mint("support-agent", "ana", {"orders:read"}, ident.API, ttl=1)
    time.sleep(2)
    revoked = ident.mint("support-agent", "ana", {"orders:read"}, ident.API)
    ident.revoke(ident.jwt.decode(revoked, options={"verify_signature": False})["jti"])
    results = [
        attempt("tampered", lambda: ident.verify(tampered, ident.API)),
        attempt("expired", lambda: ident.verify(short, ident.API)),
        attempt("wrong audience", lambda: ident.verify(good, "billing-api")),
        attempt("revoked", lambda: ident.verify(revoked, ident.API)),
    ]
    ident.disable("support-agent")
    try:
        results.append(attempt("agent disabled", lambda: ident.verify(good, ident.API)))
        results.append(attempt("analyst asks for refunds", lambda: ident.mint(
            "analyst-agent", "ana", {"refunds:create"}, ident.API)))
    finally:
        ident.DISABLED.discard("support-agent")
    for label, outcome in results:
        print(f"{label:<26} {outcome}")
    return results

if __name__ == "__main__":
    main()
