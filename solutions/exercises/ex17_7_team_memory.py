"""Exercise 17.7 (solution): shared team memory for the research team. The lead writes
agreed findings to `team` scope; workers read them and keep private `agent` notes."""
import ch17_memory_policy as mem

def lead_records(finding: str, subject: str) -> str:
    return mem.remember(finding, scope="team", owner="research", subject=subject,
                        source="agent", agent="lead")

def worker_note(worker: str, note: str) -> str:
    return mem.remember(note, scope="agent", owner=worker, source="agent", agent=worker)

def worker_tries_team_write(worker: str, text: str) -> str:
    return mem.remember(text, scope="team", owner="research", source="agent", agent=worker)

def worker_reads(worker: str, query: str) -> str:
    return mem.recall(query, owner="research", agent=worker)

if __name__ == "__main__":
    from pathlib import Path
    mem.DB = Path("memory_team_demo.db")
    mem.DB.unlink(missing_ok=True)
    print(lead_records("Hybrid search beats vector search on error codes (library/rag.md:4)",
                       subject="error code retrieval"))
    print(worker_note("worker-1", "Still need numbers for index freshness"))
    print(worker_tries_team_write("worker-2", "Vector search is always best"))
    print("worker-1 reads team:", worker_reads("worker-1", "error code search"))
    print("worker-2 reads worker-1's note:", worker_reads("worker-2", "index freshness numbers"))
