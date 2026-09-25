"""Chapter 19: check a deployed agent API from the outside, the way a user reaches it.
Run it after every deployment. It exits with an error if any check fails, so a CI
pipeline can stop a bad release.

Run:  python ch19_smoke_test.py https://your-service.example.com          (free checks)
      python ch19_smoke_test.py http://localhost:8080 --chat              (+ one real question)
Needs AGENT_API_KEY (one of the service's keys) in the environment for the authorized checks."""
import os
import sys
import time
import httpx

def check(name, ok, detail=""):
    print(f"  {'PASS' if ok else 'FAIL'}  {name}" + (f"  ({detail})" if detail else ""))
    return ok

def smoke(client: httpx.Client, url: str, key: str | None, chat: bool = False) -> bool:
    results = []
    local = any(h in url for h in ("localhost", "127.0.0.1", "testserver"))
    results.append(check("uses HTTPS", url.startswith("https://") or local,
                         "" if url.startswith("https://") else "fine locally, never in production"))
    t = time.perf_counter()
    r = client.get("/health")
    results.append(check("health endpoint answers", r.status_code == 200,
                         f"{r.status_code}, {1000 * (time.perf_counter() - t):.0f} ms"))
    body = {"message": "ping"}
    results.append(check("no key is refused", client.post("/v1/chat", json=body).status_code == 401))
    bad = client.post("/v1/chat", json=body, headers={"Authorization": "Bearer not-a-real-key"})
    results.append(check("a wrong key is refused", bad.status_code == 401))
    if "server" in {h.lower() for h in r.headers}:
        results.append(check("no server banner", False, f"Server: {r.headers['server']}"))
    if key:
        empty = client.post("/v1/chat", json={"message": ""}, headers={"Authorization": f"Bearer {key}"})
        results.append(check("bad input is rejected (422)", empty.status_code == 422))
        if chat:
            t = time.perf_counter()
            r = client.post("/v1/chat", json={"message": "How many customers are there?"},
                            headers={"Authorization": f"Bearer {key}"}, timeout=120)
            ok = r.status_code == 200 and r.json().get("answer")
            results.append(check("a real question gets an answer", bool(ok),
                                 f"{r.status_code}, {time.perf_counter() - t:.1f} s"))
    else:
        print("  SKIP  authorized checks (set AGENT_API_KEY to run them)")
    passed = all(results)
    print(f"\n{'All checks passed.' if passed else 'Some checks FAILED: do not send users here yet.'}")
    return passed

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print(__doc__)
        sys.exit(0)
    url = sys.argv[1].rstrip("/")
    key = os.environ.get("AGENT_API_KEY") or (os.environ.get("AGENT_API_KEYS", "").split(",")[0] or None)
    print(f"Smoke test: {url}")
    with httpx.Client(base_url=url, timeout=15) as client:
        sys.exit(0 if smoke(client, url, key, chat="--chat" in sys.argv) else 1)
