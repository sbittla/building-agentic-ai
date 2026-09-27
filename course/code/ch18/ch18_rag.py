"""Chapter 18: retrieval-augmented generation, built from its parts."""
import hashlib
import heapq
import json
import math
import os
import sys
import re
from pathlib import Path
import numpy as np

# ---------------------------------------------------------------- 1. chunking
def chunk_file(path: Path, root: Path, max_chars: int = 600, overlap_lines: int = 1):
    """Split a text file into chunks of whole lines (about max_chars each), keeping the
    line numbers so answers can cite (file:line)."""
    lines = path.read_text(errors="ignore").splitlines()
    chunks, start = [], 0
    while start < len(lines):
        end, size = start, 0
        while end < len(lines) and (size + len(lines[end]) <= max_chars
                                    or end == start):
            size += len(lines[end]) + 1
            end += 1
        text = "\n".join(lines[start:end]).strip()
        if text:
            chunks.append({"source": str(path.relative_to(root)), "line": start + 1,
                           "text": text})
        if end >= len(lines):
            break
        start = max(end - overlap_lines, start + 1)
    return chunks

def chunk_folder(root: str, pattern: str = "**/*.md", **kw):
    root = Path(root)
    return [c for p in sorted(root.glob(pattern)) if p.is_file()
            for c in chunk_file(p, root, **kw)]

# ---------------------------------------------------------------- 2. embeddings
class HashingEmbedder:
    """Offline and free, but LEXICAL only: similar words, not similar meanings.
    Good for tests and for learning the mechanics."""
    name, dims = "hashing", 512

    def embed(self, texts, input_type="document"):
        out = np.zeros((len(texts), self.dims), dtype=np.float32)
        for i, t in enumerate(texts):
            words = re.findall(r"\w+", t.lower())
            feats = words + [w[j:j + 3] for w in words
                             for j in range(max(1, len(w) - 2))]
            for f in feats:
                h = int(hashlib.md5(f.encode()).hexdigest(), 16)
                out[i, h % self.dims] += 1 if (h >> 64) % 2 else -1
        norms = np.linalg.norm(out, axis=1, keepdims=True)
        return out / np.maximum(norms, 1e-9)

class LocalEmbedder:
    """A small semantic model that runs on your CPU (model2vec, ~30 MB, downloaded
    once)."""
    name = "local"

    def __init__(self, model="minishlab/potion-base-8M"):
        from model2vec import StaticModel
        self.model = StaticModel.from_pretrained(model)

    def embed(self, texts, input_type="document"):
        v = np.asarray(self.model.encode(list(texts)), dtype=np.float32)
        return v / np.maximum(np.linalg.norm(v, axis=1, keepdims=True), 1e-9)

class VoyageEmbedder:
    """Hosted embeddings from Voyage AI (needs VOYAGE_API_KEY)."""
    name = "voyage"

    def __init__(self, model="voyage-4-lite"):
        import voyageai
        self.client, self.model = voyageai.Client(), model

    def embed(self, texts, input_type="document"):
        v = np.asarray(self.client.embed(list(texts), model=self.model,
                                         input_type=input_type).embeddings,
                       dtype=np.float32)
        return v / np.maximum(np.linalg.norm(v, axis=1, keepdims=True), 1e-9)

def get_embedder(name: str | None = None):
    name = name or os.environ.get("EMBEDDER", "auto")
    if name == "voyage" or (name == "auto" and os.environ.get("VOYAGE_API_KEY")):
        return VoyageEmbedder()
    if name in ("local", "auto"):
        try:
            return LocalEmbedder()
        except Exception as exc:
            if name == "local":
                raise
            print(f"(local embedding model unavailable: {type(exc).__name__}; "
                  "using hashing)")
    return HashingEmbedder()

# ------------------------------------------------------------- 3. keyword search (BM25)
class BM25:
    def __init__(self, texts, k1=1.5, b=0.75):
        self.docs = []
        total_len = 0
        df = {}

        # SINGLE PASS: tokenize, sum lengths, count document frequency
        for t in texts:
            words = re.findall(r"\w+", t.lower())
            self.docs.append(words)
            total_len += len(words)

            # Count each unique word's document frequency
            for w in set(words):
                df[w] = df.get(w, 0) + 1

        self.k1, self.b = k1, b
        self.avg = total_len / max(len(self.docs), 1)
        n = len(self.docs)
        self.idf = {w: math.log(1 + (n - c + 0.5) / (c + 0.5)) for w, c in df.items()}

    def scores(self, query):
        q = re.findall(r"\w+", query.lower())
        out = []
        for d in self.docs:
            s = 0.0
            for w in q:
                f = d.count(w)
                if f:
                    s += self.idf.get(w, 0) * f * (self.k1 + 1) / (
                        f + self.k1 * (1 - self.b + self.b * len(d) / self.avg))
            out.append(s)
        return np.array(out)

# ---------------------------------------------------------------- 4. the index
class Index:
    def __init__(self, chunks, embedder):
        self.chunks, self.embedder = chunks, embedder
        self.vectors = (embedder.embed([c["text"] for c in chunks]) if chunks
                        else np.zeros((0, 1)))
        self.bm25 = BM25([c["text"] for c in chunks])

    def save(self, path="rag_index"):
        np.save(f"{path}.npy", self.vectors)
        Path(f"{path}.json").write_text(json.dumps({"embedder": self.embedder.name,
                                                    "chunks": self.chunks}))

    @classmethod
    def load(cls, path="rag_index", embedder=None):
        meta = json.loads(Path(f"{path}.json").read_text())
        self = cls.__new__(cls)
        self.chunks, self.vectors = meta["chunks"], np.load(f"{path}.npy")
        self.embedder = embedder or get_embedder(meta["embedder"])
        self.bm25 = BM25([c["text"] for c in self.chunks])
        return self

    def vector_ranks(self, query, k=None):
        q = self.embedder.embed([query], input_type="query")[0]
        # cosine: vectors are unit length
        top_indices = np.argsort(-(self.vectors @ q))
        if k is not None:
            return list(top_indices[:k])
        return list(top_indices)

    def keyword_ranks(self, query, k=None):
        scores = self.bm25.scores(query)
        top_indices = np.argsort(-scores)
        if k is not None:
            return list(top_indices[:k])
        return list(top_indices)

    def search(self, query, k=5, mode="hybrid"):
        if mode == "vector":
            order = self.vector_ranks(query, k=k)
        elif mode == "keyword":
            order = self.keyword_ranks(query, k=k)
        else:                                                   # reciprocal rank fusion
            # Blend top-3k candidates from both methods
            blend_k = max(k * 3, 20)  # Balance: wider blend for better quality
            vector_order = self.vector_ranks(query, k=blend_k)
            keyword_order = self.keyword_ranks(query, k=blend_k)

            fused = {}
            for r, i in enumerate(vector_order):
                fused[i] = fused.get(i, 0) + 1 / (60 + r)
            for r, i in enumerate(keyword_order):
                fused[i] = fused.get(i, 0) + 1 / (60 + r)

            # Use heap to get top-k efficiently: O(n log k)
            order = heapq.nlargest(k, fused, key=fused.get)

        return [self.chunks[i] for i in order]

# -------------------------------------------------------------- 5. RAG as an agent tool
_index = None

def search_knowledge(query: str, k: int = 4) -> str:
    """Tool: the best matching passages, each with a (file:line) citation."""
    hits = _index.search(query, k=k)
    return "\n\n".join(f"({h['source']}:{h['line']})\n{h['text']}"
                       for h in hits) or "No results."

TOOLS = [{"name": "search_knowledge", "description": "Search the team knowledge base "
          "(notes and library) by meaning and keywords. Returns passages with "
          "(file:line) citations. Search before answering; search again with other "
          "words if results look off.",
          "input_schema": {"type": "object", "properties": {"query": {"type": "string"},
                           "k": {"type": "integer"}}, "required": ["query"]}}]
SYSTEM = ("Answer from the knowledge base only. Cite every fact as (file:line) exactly "
          "as the search results show it. If the passages don't answer the question, "
          "say so.")

def run_tool(name, args):
    try:
        return (search_knowledge(**args) if name == "search_knowledge"
                else f"ERROR: unknown tool {name}")
    except Exception as exc:
        return f"ERROR: {type(exc).__name__}: {exc}"

def build(roots=("notes", "library"), embedder=None):
    global _index
    chunks = []
    for r in roots:
        for c in chunk_folder(r):
            c["source"] = f"{r}/{c['source']}"
            chunks.append(c)
    _index = Index(chunks, embedder or get_embedder())
    return _index

# -------------------------------------------------------------- 6. evaluating retrieval
EVAL = [  # (question, the file that answers it)
    ("What caused the consumer lag spike?",
     "notes/work/2026-06-02-incident-kafka-lag.md"),
    ("When do we remove ZooKeeper?", "notes/work/2026-07-15-kafka-upgrade-plan.md"),
    ("Why did checkout get slower after the May release?",
     "notes/work/2026-05-10-latency-review.md"),
    ("How fast must the primary on-call respond?",
     "notes/work/2026-08-01-on-call-handbook.md"),
    ("How much table bloat did we fix?", "notes/work/2026-04-18-postgres-vacuum.md"),
    ("What was the bottleneck in the search load test?",
     "notes/work/2026-03-03-load-test-results.md"),
    ("Where is the router admin page?", "notes/personal/home-network.md"),
    ("What should I pack for the conference trip?", "notes/personal/travel-2026.md"),
    ("Which search misses exact error codes like ERR-4471?", "library/error-codes.md"),
    ("Why do stale indexes give wrong answers?", "library/freshness.md"),
    ("How do I keep agent costs predictable?", "library/cost-of-agents.md"),
    ("Is multi-agent a good fit for coding tasks?", "library/multi-agent.md"),
]

def evaluate(index, k=3, modes=("keyword", "vector", "hybrid")):
    """Recall@k (right file in the top k) and MRR (1 / rank of the first right file)."""
    report = {}
    for mode in modes:
        hits, rr = 0, 0.0
        for q, expected in EVAL:
            ranked = [c["source"] for c in index.search(q, k=20, mode=mode)]
            if expected in ranked[:k]:
                hits += 1
            rr += 1 / (ranked.index(expected) + 1) if expected in ranked else 0
        report[mode] = {"recall@k": round(hits / len(EVAL), 2),
                        "mrr": round(rr / len(EVAL), 2)}
    return report

if __name__ == "__main__":
    # python ch18_rag.py                  build, evaluate, then ask the agent a question
    # python ch18_rag.py eval             build and evaluate only (no API key needed)
    # python ch18_rag.py search "query"   show the top 3 results in every mode
    args = sys.argv[1:]
    try:
        index = build()
    except Exception as exc:
        sys.exit(f"Could not load the {os.environ.get('EMBEDDER', 'auto')} embedder "
                 f"({type(exc).__name__}: {exc}).\nThe local model downloads once "
                 "from Hugging Face; if that's blocked, use EMBEDDER=hashing (or "
                 "voyage with VOYAGE_API_KEY).")
    print(f"{len(index.chunks)} chunks, embedder = {index.embedder.name}")
    if args[:1] == ["search"]:
        query = " ".join(args[1:]) or "temperature units"
        for mode in ("keyword", "vector", "hybrid"):
            print(f"\n{mode}:")
            for c in index.search(query, k=3, mode=mode):
                print(f"  ({c['source']}:{c['line']})  {c['text'][:70]!r}")
        sys.exit(0)
    for mode, r in evaluate(index).items():
        print(f"  {mode:<8} recall@3 = {r['recall@k']}  MRR = {r['mrr']}")
    if args[:1] != ["eval"]:
        from ch04_agent import run_agent
        print(run_agent("What caused the Kafka lag incident, and what did we change?",
                        TOOLS, run_tool, system=SYSTEM)[0])
