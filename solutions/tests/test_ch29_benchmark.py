"""Chapter 29.8: the architecture benchmark. Offline: the simulator backend."""
import json

import pytest


@pytest.fixture
def bench(ws):
    import ch29_benchmark as b
    saved = {k: dict(v) for k, v in b.SIM_MODELS.items()}
    yield b
    for k, v in saved.items():
        b.SIM_MODELS[k].update(v)


def t(*segments, ok=True):
    return {"trace": list(segments), "result": {"ok": ok, "cost": 1.0}}


def test_replay_queues_for_slots_first_come_first_served(bench):
    tasks = [t(("model", 100)), t(("model", 100)), t(("tool", 50), ("model", 100))]
    out, makespan = bench.replay(tasks, workers=3, slots=1)
    by_ms = sorted(r["ms"] for r in out)
    assert by_ms == [100, 200, 300] and makespan == 300          # one slot: strictly in turn
    assert sorted(r["queue_ms"] for r in out) == [0, 100, 150]   # the third waited from 50 to 200


def test_replay_closed_loop_and_parallel_slots(bench):
    tasks = [t(("model", 100), ("tool", 100)) for _ in range(4)]
    out, makespan = bench.replay(tasks, workers=2, slots=2)
    assert makespan == 400 and all(r["queue_ms"] == 0 for r in out)   # two at a time, no waiting


def test_replay_gives_up_after_the_queue_deadline(bench):
    tasks = [t(("model", 5_000)), t(("model", 100))]
    out, _ = bench.replay(tasks, workers=2, slots=1, deadline_ms=1_000)
    failed = [r for r in out if not r["ok"]]
    assert len(failed) == 1 and failed[0]["error"] == "queue timeout" and failed[0]["ms"] == 1_000
    assert failed[0]["cost"] == 0                                # never got a model call


def test_simulator_is_exactly_reproducible(bench, tmp_path):
    args = ["--quick", "--experiments", "E1,E2,E4", "--concurrency", "1,4", "--quiet"]
    first = bench.main(args + ["--out", str(tmp_path / "a")])
    second = bench.main(args + ["--out", str(tmp_path / "b")])
    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)
    e1 = {r["config"]: r for r in first["E1"]}
    assert e1["workflow"]["model_calls"] < e1["agent"]["model_calls"] < e1["multi-agent"]["model_calls"]
    e2 = {r["config"]: r for r in first["E2"]}
    assert e2["tools parallel"]["p50_s"] < e2["tools sequential"]["p50_s"]
    run = next((tmp_path / "a").iterdir())
    config = json.loads((run / "config.json").read_text())
    for key in ("commit", "prompts_sha256", "data_fingerprint", "seed", "reps", "platform", "simulated_models"):
        assert key in config
    assert sum(1 for _ in open(run / "raw.jsonl")) > 0 and (run / "summary.md").exists()


def test_success_means_the_right_answer(bench):
    single, _ = bench.load_cases()
    case = next(c for c in single if c["id"] == "order-count")
    right = bench.expected(case)[0]
    assert bench.correct(case, f"There are {right} orders.")
    assert not bench.correct(case, f"There are {right + 7} orders.")


def test_failed_tools_are_retried_and_counted(bench, ws):
    _, multi = bench.load_cases()
    for c in multi:
        bench.QUESTIONS[c["question"]] = c["sqls"]
    r = bench.task(multi[0], "agent", backend=bench.VirtualTime(), client_for=bench.SimClient,
                   model=bench.LARGE, seed_key="t", fail_rate=1.0, tool_ms=100)
    assert r["tool_errors"] >= 1 and not r["ok"]                 # every call fails: no answer
