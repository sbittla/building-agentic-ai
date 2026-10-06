"""Chapter 28.13: correlating spans with resource samples and profiler stacks.
All offline: the traffic is ch28_profile.synthetic(), seeded."""
import pytest

import ch28_profile as p


@pytest.fixture(scope="module")
def traffic():
    spans, samples, stacks = p.synthetic()
    rows = p.attribute(spans, samples)
    return spans, samples, stacks, rows, p.correlate(rows)


def test_normalize_reads_both_span_shapes():
    otel = {"name": "execute_tool run_sql", "trace_id": "t", "span_id": "s1",
            "start_ms": 100, "ms": 250,
            "attributes": {"gen_ai.tool.name": "run_sql", "db.rows": 40}}
    simple = {"name": "plan", "kind": "model", "trace_id": "t", "start_ms": 0,
              "end_ms": 900, "tokens": 120}
    a, b = p.normalize(otel), p.normalize(simple)
    assert (a["kind"], a["group"], a["end"], a["ms"], a["rows"]) == \
        ("tool", "run_sql", 350, 250, 40)
    assert (b["kind"], b["group"], b["ms"], b["tokens_out"]) == ("model", "model", 900, 120)


def test_resources_are_weighted_by_overlap():
    samples = [{"t": 0, "cpu": 50, "db_ms": 20}, {"t": 1000, "cpu": 90, "db_ms": 20}]
    span = {"start": 500, "end": 1500}
    r = p.resources_during(span, samples)
    assert r["mean"] == {"cpu": 70.0, "db_ms": 20.0}
    assert r["saturated"] == {"cpu": 0.5, "db_ms": 0.0}
    late = p.resources_during({"start": 800, "end": 1800}, samples)
    assert late["mean"]["cpu"] == 82.0 and late["saturated"]["cpu"] == 0.8
    assert p.resources_during({"start": 5000, "end": 6000}, samples)["mean"] == {}


def test_attribute_skips_the_run_and_counts_ms_under_saturation():
    samples = [{"t": 0, "cpu": 95}, {"t": 1000, "cpu": 40}]
    spans = [{"name": "invoke_agent", "trace_id": "t", "start_ms": 0, "ms": 2000},
             {"name": "execute_tool draw", "trace_id": "t", "start_ms": 600, "ms": 1000}]
    (row,) = p.attribute(spans, samples)
    assert row["group"] == "draw" and row["ms_under"] == {"cpu": 400.0}
    assert row["saturated_by"] == []                  # 40% of the span: under min_share
    assert p.attribute(spans, samples, min_share=0.4)[0]["saturated_by"] == ["cpu"]


def test_rank_corr():
    assert p.rank_corr([1, 2, 3, 4], [10, 20, 30, 400]) == 1.0
    assert p.rank_corr([1, 2, 3, 4], [4, 3, 2, 1]) == -1.0
    assert p.rank_corr([5, 5, 5, 5], [1, 2, 3, 4]) == 0.0      # no variation: no claim
    assert p._ranks([3, 1, 3, 2]) == [2.5, 0.0, 2.5, 1.0]      # ties share a rank


def test_synthetic_is_reproducible():
    a, b = p.synthetic(), p.synthetic()
    assert a == b
    spans, samples, stacks = a
    assert len(samples) == 600 and len(stacks) > 10_000
    assert sum(s["name"] == "invoke_agent" for s in spans) > 250


def test_correlation_finds_the_injected_causes(traffic):
    *_, corr = traffic
    sql, chart, model = corr["run_sql"], corr["render_chart"], corr["model"]
    assert sql["r"]["db_ms"] > 0.8 and abs(sql["r"]["cpu"]) < 0.2
    assert sql["saturated"]["db_ms"]["lift"] > 5 and sql["saturated"]["cpu"]["lift"] < 1.2
    assert chart["saturated"]["cpu"]["lift"] > 2
    assert chart["saturated"]["db_ms"]["lift"] < 1.2
    assert model["r"]["tokens_out"] > 0.9 and abs(model["r"]["gpu"]) < 0.2


def test_diagnosis_names_the_right_resource(traffic):
    lines = p.diagnose(traffic[-1])
    sql = next(l for l in lines if "`run_sql`" in l)
    chart = next(l for l in lines if "`render_chart`" in l)
    assert "the database is busy" in sql and "not when the CPU" in sql
    assert "the CPU is busy" in chart and "not when the database" in chart
    assert any(l.startswith("model calls: latency follows output tokens") for l in lines)
    assert any(l.startswith("queue waits") and "nothing to explain" in l for l in lines)


def test_diagnosis_needs_both_lift_and_correlation():
    corr = {"t": {"n": 100, "p95": 900, "r": {"cpu": 0.8},
                  "saturated": {"cpu": {"n": 6, "p50_hot": 200, "p50_cold": 190,
                                        "lift": 1.1}}}}
    assert "no resource" in p.diagnose(corr)[0]      # correlated, but no slower
    corr["t"]["r"]["cpu"] = 0.1
    corr["t"]["saturated"]["cpu"]["lift"] = 3.0
    assert "no resource" in p.diagnose(corr)[0]      # slower, but no correlation
    corr["t"]["r"]["cpu"] = 0.6
    assert "the CPU is busy" in p.diagnose(corr)[0]


def test_profile_of_the_slowest_spans(traffic):
    _, _, stacks, rows, _ = traffic
    worst = p.slowest(rows, "run_sql")
    assert worst and all("db_ms" in r["saturated_by"] for r in worst)
    assert p.top_frames(stacks, worst, 1)[0][:2] == ("socket.recv", "cursor.execute")
    rest = p.slowest(rows, "run_sql", unexplained=True)
    assert rest and not any(r["saturated_by"] for r in rest)
    assert p.top_frames(stacks, rest, 1)[0][:2] == ("json.dumps", "rows_to_json")


def test_top_frames_joins_on_time_without_span_ids():
    spans = [{"span_id": None, "start": 0, "end": 100}]
    stacks = [{"t": 10, "stack": ["a", "b"]}, {"t": 50, "stack": ["a", "b"]},
              {"t": 90, "stack": ["a", "c"]}, {"t": 150, "stack": ["a", "d"]}]
    assert p.top_frames(stacks, spans) == [("b", "a", 0.667), ("c", "a", 0.333)]


def test_exercise_28_8_network_incident():
    import ex28_8_network as ex
    spans, samples, stacks = ex.with_network_incident()
    lines = p.diagnose(p.correlate(p.attribute(spans, samples)))
    fx = next(l for l in lines if "`fx_rates`" in l)
    assert "the network is busy" in fx
    assert any("`run_sql` is slow when the database is busy" in l for l in lines)
    worst, by_id, by_time = ex.frames_with_and_without_ids(spans, samples, stacks)
    assert by_id[0][0] == "socket.recv" and by_id[0][2] > 0.8
    assert by_time[0][0] != "socket.recv"              # other requests' stacks win
