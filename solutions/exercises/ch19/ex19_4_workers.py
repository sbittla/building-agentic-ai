"""Exercise 19.4 (solution): two workers share a queue of jobs. One dies holding a job;
when its lease runs out, the other worker claims the job and finishes it."""
import threading
import time

import ch19_durable as d

def open_jobs() -> int:
    with d._db() as con:
        return con.execute("SELECT COUNT(*) FROM jobs WHERE status IN "
                           "('queued','running')").fetchone()[0]

def worker(name: str, finished: dict, crash_first: bool = False):
    """Claim, run, repeat. With crash_first, die after one step of the first job."""
    while open_jobs():
        job = d.claim(name)
        if job is None:                 # everything left is leased: wait and look again
            time.sleep(0.05)
            continue
        try:
            d.run_job(job, worker=name, crash_after=1 if crash_first else None)
            finished[job] = name
        except d.Crash:
            return                      # a dead worker never releases its lease

def main(n_jobs: int = 5, lease: float = 0.5):
    d.LEASE, d.BACKOFF, d.FAILS["charge"] = lease, 0.01, 0
    jobs = [d.create_job(f"customer {i}",
                         [{"action": "create_account", "args": {"email": f"c{i}@x.io"}},
                          {"action": "charge", "args": {"email": f"c{i}@x.io",
                                                        "amount": 10}}])
            for i in range(n_jobs)]
    finished = {}
    threads = [threading.Thread(target=worker, args=("w1", finished, True)),
               threading.Thread(target=worker, args=("w2", finished))]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=30)
    for job in jobs:
        print(d.report(job))
    print("finished by:", finished)
    return jobs, finished

if __name__ == "__main__":
    main()
