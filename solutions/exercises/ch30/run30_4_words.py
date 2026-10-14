"""Exercise 30.4, run end to end against sol_ch30_service: stream the answer from
/v1/chat/stream_text and show each piece as it arrives, with its arrival time."""
import time

import httpx
from ch30_client import API, KEY

if __name__ == "__main__":
    t0, pieces = time.perf_counter(), []
    with httpx.stream("POST", f"{API}/v1/chat/stream_text",
                      json={"message": "Which product category earns the most revenue? "
                                       "Explain in two sentences."},
                      headers={"Authorization": f"Bearer {KEY}"}, timeout=300) as r:
        if r.status_code == 404:
            raise SystemExit("The service has no /v1/chat/stream_text endpoint yet: "
                             "that's exercise 30.4.")
        r.raise_for_status()
        for piece in r.iter_text():
            pieces.append(piece)
            print(f"{time.perf_counter() - t0:6.2f}s  {piece!r}", flush=True)
    span = time.perf_counter() - t0
    print(f"\nanswer: {''.join(pieces)}")
    print(f"arrived in {len(pieces)} pieces over {span:.1f} s")
