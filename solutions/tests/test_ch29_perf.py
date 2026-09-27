"""Chapter 29 performance engineering: latency and cost models, the concurrency
experiment on the simulated agent, and exercise 29.6 with the scripted model."""
from functools import partial

import pytest
from fakemodel import text, tool, tool_results

def test_latency_model_from_spans_sums_to_total():
    import ch29_perf as p
    spans = [{"name": "invoke_agent", "ms": 1000, "attributes": {}},
             {"name": "chat claude-sonnet-5", "ms": 400, "attributes": {}},
             {"name": "chat claude-sonnet-5", "ms": 300, "attributes": {}},
             {"name": "execute_tool run_query", "ms": 100,
              "attributes": {"gen_ai.tool.name": "run_query"}},
             {"name": "execute_tool get_schema", "ms": 50,
              "attributes": {"gen_ai.tool.name": "get_schema"}},
             {"name": "queue wait_for_slot", "ms": 20, "attributes": {}}]
    lm = p.latency_model(spans, serialize_ms_per_step=2)
    assert lm == {"model": 700, "tool": 50, "retrieval": 100, "queueing": 20,
                  "serialization": 4, "orchestration": 126, "total": 1000}
    parts = [v for k, v in lm.items() if k != "total"]
    assert sum(parts) == pytest.approx(lm["total"])
    measured = p.latency_model({"total_ms": 900.0, "model_ms": 500.5, "tool_ms": 10,
                                "retrieval_ms": 90, "queue_ms": 0, "serialize_ms": 7,
                                "steps": 3})
    assert measured["serialization"] == 7 and measured["orchestration"] == 292.5
    assert "= 1,000 ms" in p.format_latency(lm)
    assert p.is_retrieval("search_docs") and not p.is_retrieval("get_schema")

def test_cost_per_task_components():
    import ch29_perf as p
    c = p.cost_per_task(input_tokens=10_000, cached_tokens=6_000,
                        cache_write_tokens=1_000, output_tokens=500, model_calls=3,
                        tool_calls=2, tool_price=0.01, retrieval_calls=3,
                        retrieval_price=0.002, retries=1, infra_per_hour=3.6,
                        tasks_per_hour=360, review_share=0.1, review_minutes=6,
                        reviewer_per_hour=50)
    # 3,000 fresh x $2 + 6,000 read x $0.20 + 1,000 written x $2.50 + 500 out x $10
    assert c["model"] == pytest.approx(0.0147)
    assert c["tool"] == 0.02 and c["retrieval"] == 0.006 and c["infra"] == 0.01
    assert c["retry"] == pytest.approx(0.0049) and c["review"] == pytest.approx(0.5)
    assert c["total"] == pytest.approx(sum(v for k, v in c.items() if k != "total"))
    assert p.cost_per_task(input_tokens=1000)["infra"] == 0.0     # no rate, no infra

def test_experiment_finds_the_knee():
    import ch29_perf as p
    patient = partial(p.simulated_agent, sim={**p.SIM, "queue_deadline_ms": 1e9})
    rows = p.experiment(patient, ["q"], (1, 2, 4, 8), n=24, model_slots=2,
                        scale=0.004)
    by = {r["concurrency"]: r for r in rows}
    assert by[2]["throughput"] > 1.6 * by[1]["throughput"]       # rising...
    assert by[8]["throughput"] < 1.3 * by[2]["throughput"]       # ...then flat
    assert by[8]["p95_s"] > 1.5 * by[2]["p95_s"]                 # queueing instead
    assert by[1]["queue_ms"] < 100 < 1000 < by[8]["queue_ms"]
    assert all(r["success"] == 1 and r["cache_hit"] > 0.5 for r in rows)
    assert by[1]["tokens"] == by[8]["tokens"]      # same seeded work at every level
    assert p.knee(rows)["concurrency"] <= 4
    table = p.format_experiment(rows)
    assert len(table.splitlines()) == len(rows) + 2
    assert max(len(line) for line in table.splitlines()) <= 88

def test_queue_deadline_costs_successes():
    import ch29_perf as p
    rows = p.experiment(p.simulated_agent, ["q"], (1, 8), n=16, model_slots=1,
                        scale=0.004)
    assert rows[0]["success"] == 1 and rows[1]["success"] < 0.8
    assert rows[1]["cost_per_success"] > rows[0]["cost_per_success"]
    assert rows[1]["goodput"] < rows[1]["throughput"]

def test_29_6_experiment(model, ws, monkeypatch):
    import ch04_agent
    import ex29_6_experiment as ex
    monkeypatch.setattr(ch04_agent, "_client", None)     # restored after the test
    def analyst(kw):                        # schema, then a count, then the answer
        turn = sum(m["role"] == "assistant" for m in kw["messages"])
        if turn == 0:
            return [tool("get_schema", {})]
        if turn == 1:
            return [tool("run_query", {"sql": "SELECT COUNT(*) FROM orders"})]
        return [text(f"The answer is {tool_results(kw)[0]}.")]
    model.reset(default=analyst)
    rows = ex.main(levels=(1, 2), n=4)
    assert [r["concurrency"] for r in rows] == [1, 2]
    assert len(model.calls) == 2 * 4 * 3
    for r in rows:
        assert r["tasks"] == 4 and r["success"] == 1 and r["steps"] == 3
        assert r["tokens"] == 3 * 120                    # fake usage: 100 in, 20 out
        assert r["cost"] == pytest.approx(3 * 0.0004)
        assert r["retrieval_ms"] > 0 and r["tool_ms"] > 0   # run_query, get_schema
    one = rows[0]["results"][0]
    assert one["tool_calls"] == 1 and one["retrieval_calls"] == 1
