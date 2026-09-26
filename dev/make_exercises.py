"""Dev tool: build course/exercises.json from the course markdown + a run map."""
import json
import re
import sys
from pathlib import Path

MD = Path(sys.argv[1])            # folder with the book's markdown chapters
OUT = Path(sys.argv[2])

# kind: concept | run | ask | build | test | inspector | desktop
#   run       -> shell command in /workspace
#   ask       -> chat with a chapter's tools: module [question]
#   build     -> starter file exercises/<name>.py, then run it
#   test      -> starter test tests/<name>.py, then pytest it
#   inspector -> MCP Inspector against a server file
#   desktop   -> print Claude Desktop config
R = lambda cmd, **kw: {"kind": "run", "cmd": cmd, **kw}
A = lambda mod, q=None, **kw: {"kind": "ask", "module": mod, "question": q, **kw}
B = lambda name, **kw: {"kind": "build", "file": f"exercises/{name}.py", **kw}
T = lambda name, **kw: {"kind": "test", "file": f"tests/{name}.py", **kw}

MAP = {
    # ---- chapter 0 and the interludes (T = testing, R = regex, S = SQL, A = async)
    "0.3": R("test -f hello.py && python hello.py || echo 'Create workspace/hello.py on your computer first, then run this again.'"),
    "0.4": B("ex0_4_basics"),
    "0.5": B("ex0_5_forecast"),
    "0.6": B("ex0_6_city_temperature"),
    "0.7": B("ex0_7_expenses"),
    "P.1": B("exP_1_comprehensions"),
    "P.2": B("exP_2_run_tool"),
    "P.3": B("exP_3_tasklist"),
    "P.4": B("exP_4_decorators"),
    "P.5": B("exP_5_bugs"),
    "T.1": R("python -m pytest -q test_i_pricing.py", edit=["i_pricing.py"]),
    "T.2": T("test_exT_2_parametrize"),
    "T.3": T("test_ex_t3"),
    "T.4": T("test_exT_4_fake_network"),
    "R.1": B("exR_1_logs"),
    "R.2": B("exR_2_mask"),
    "R.3": B("exR_3_citations"),
    "R.4": B("exR_4_error_codes"),
    "S.1": B("exS_1_warmup"),
    "S.2": B("exS_2_fix_query"),
    "S.3": B("exS_3_business"),
    "S.4": B("exS_4_parameters"),
    "A.1": B("exA_1_measure"),
    "A.2": B("exA_2_fixed"),
    "A.3": B("exA_3_semaphore"),
    "A.4": B("exA_4_timeouts"),
    "1.3": R("python ch01_summarize.py", edit=["ch01_summarize.py"]),
    "1.7": {"kind": "concept"},  # a written design note
    "1.4": R("python ch01_where_llms_fail.py"),
    "1.5": B("ex1_5_workflow"),
    "1.6": B("ex1_6_chat"),
    "2.3": R("python ch02_calculator_agent.py", edit=["ch02_calculator_agent.py"]),
    "2.4": B("ex2_4_description_eval"),
    "2.5": T("test_ex2_5_errors", edit=["ch02_calculator_agent.py"]),
    "2.6": B("ex2_6_two_tools"),
    "3.3": A("ch03_tools", "What time is it in Tokyo?", edit=["ch03_tools.py"]),
    "3.4": R("python ch03_routing_eval.py", edit=["ch03_routing_eval.py"]),
    "3.5": B("ex3_5_forced_tool"),
    "3.6": R("python ch03_routing_eval.py", edit=["ch03_tools.py", "ch03_routing_eval.py"]),
    "3.7": R("python ch03_tool_search.py"),
    "4.2": R("python ch04_agent.py"),
    "4.3": B("ex4_3_cap"),
    "4.4": B("ex4_4_tracer"),
    "4.5": B("ex4_5_cost_profile"),
    "5.3": R("python ch05_todo_tools.py"),
    "5.4": R("python ch05_todo_tools.py", edit=["ch05_todo_tools.py"]),
    "5.5": R("python ch05_todo_tools.py", edit=["ch05_todo_tools.py"]),
    "5.6": R("python ch05_todo_tools.py"),
    "5.7": T("test_ex5_7_sqlite", edit=["ch05_todo_tools.py"]),
    "6.2": A("ch06_notes_tools"),
    "6.3": T("test_ex6_3_sandbox"),
    "6.4": B("ex6_4_citation_checker"),
    "6.5": A("ch06_notes_tools", "What did I write about Kafka in July 2026?", edit=["ch06_notes_tools.py"]),
    "6.6": B("ex6_6_scale_test", setup="course data notes --count 2000 --out notes_big"),
    "7.3": A("ch07_weather_tools"),
    "7.4": A("ch07_weather_tools", edit=["ch07_weather_tools.py"]),
    "7.5": B("ex7_5_parallel"),
    "7.6": B("ex7_6_trip_benchmark"),
    "8.3": R("python ch08_sql_tools.py"),
    "8.4": A("ch08_sql_tools", edit=["ch08_sql_tools.py"]),
    "8.5": A("ch08_sql_tools", edit=["ch08_sql_tools.py"]),
    "8.6": A("ch08_sql_tools", edit=["ch08_sql_tools.py"]),
    "8.7": B("ex8_7_eval_harness"),
    "9.3": R("python ch09_organizer.py", setup="course data messy --count 15"),
    "9.4": R("python ch09_organizer.py"),
    "9.5": R("python ch09_organizer.py", edit=["ch09_organizer.py"]),
    "9.6": T("test_ex9_6_policy", setup="course data messy --count 200 --out messy_big"),
    "10.3": R("python ch10_fixer.py", setup="course data repo --fresh"),
    "10.4": R("python ch10_fixer.py", setup="course data repo --fresh", edit=["ch10_fixer.py"]),
    "10.5": R("python ch10_fixer.py", edit=["ch10_fixer.py"]),
    "10.6": R("python ch10_fixer.py", setup="course data repo --fresh", edit=["ch10_fixer.py"]),
    "10.7": B("ex10_7_benchmark", needs="sandbox"),
    "11.3": R("python ch11_research_team.py"),
    "11.4": R("python ch11_research_team.py", edit=["ch11_research_team.py"]),
    "11.5": R("python ch11_research_team.py", edit=["ch11_research_team.py"]),
    "11.6": B("ex11_6_compare"),
    "11.7": R("python ch11_patterns.py"),
    "12.3": {"kind": "inspector", "server": "ch12_weather_server.py"},
    "12.4": {"kind": "inspector", "server": "ch12_weather_server.py", "edit": ["ch12_weather_server.py"]},
    "12.5": {"kind": "desktop", "server": "ch12_weather_server.py"},
    "12.6": {"kind": "inspector", "server": "exercises/ex12_6_calc_server.py", "stub": True},
    "12.7": T("test_ex12_7_http"),
    "13.2": B("ex13_2_client"),
    "13.3": R("python ch13_mcp_agent.py servers.json"),
    "13.4": R("python ch13_mcp_agent.py servers.json", edit=["ch13_mcp_agent.py"]),
    "13.5": R("python ch13_mcp_agent.py servers.json", edit=["servers.json"]),
    "13.6": R("python ch13_mcp_agent.py servers.json", edit=["ch13_mcp_agent.py"]),
    "13.7": B("ex13_7_host"),
    "13.8": B("ex13_8_coordinator"),
    "13.9": B("ex13_9_a2a_team"),
    "14.3": R("python ch14_policy_agent.py servers_github.json", needs="github"),
    "14.4": R("python ch14_policy_agent.py servers_github.json", needs="github"),
    "14.5": R("python ch14_policy_agent.py servers_ecosystem.json", edit=["ch13_mcp_agent.py"]),
    "14.6": B("ex14_6_redteam"),
    "27.3": R("python ch27_eval.py eval_sql.jsonl 3", edit=["eval_sql.jsonl"]),
    "29.1": R("python ch29_loadtest.py 4 && python ch29_loadtest.py 8 && python ch29_loadtest.py 12",
              edit=["ch29_loadtest.py"]),
    "27.4": B("ex27_4_ci_gate"),
    "28.1": B("ex28_1_trace_report"),
    "29.2": B("ex29_2_real_loadtest"),
    "27.5": B("ex27_5_calibrate"),
    # ---- Part 6
    "16.3": R("python ch16_context.py", edit=["ch16_context.py"]),
    "16.4": R("python ch16_assemble.py", edit=["ch16_assemble.py"]),
    "16.6": T("test_ex16_6_fresh", edit=["ch16_assemble.py"]),
    "16.8": B("ex16_8_briefed_team"),
    "17.4": R("python ch17_memory_policy.py", edit=["ch17_memory_policy.py"]),
    "17.5": B("ex17_5_consolidate"),
    "17.6": B("ex17_6_poison"),
    "17.7": B("ex17_7_team_memory"),
    "18.7": B("ex18_7_weather_source"),
    "18.8": B("ex18_8_know_when_to_stop"),
    "18.9": B("ex18_9_verified"),
    "17.3": R("python ch17_memory.py"),
    "16.5": B("ex16_5_cache_savings"),
    "17.8": B("ex17_8_assistant"),
    "16.7": R("python ch16_programmatic.py"),
    "18.3": R("python ch18_rag.py search temperature units && python ch18_rag.py search ERR-4471"),
    "18.4": R("EMBEDDER=hashing python ch18_rag.py eval && EMBEDDER=local python ch18_rag.py eval"),
    "18.5": B("ex18_5_paraphrased"),
    "18.6": B("ex18_6_knowledge_agent"),
    "24.3": R("python ch24_agent_sdk.py Delete all cancelled orders."),
    "24.4": B("ex24_4_sdk_mcp"),
    "24.5": B("ex24_5_three_ways"),
    "24.6": R("python ch24_skills.py"),
    "24.7": R("python ch24_managed_agent.py"),
    "30.2": R("python ch30_client.py && python ch30_client.py stream"),
    "30.3": R("python ch30_client.py limits"),
    "30.4": R("python ch30_client.py words", edit=["ch30_service.py", "ch30_client.py"]),
    "30.5": B("ex30_5_remote_hub"),
    "30.6": B("ex30_6_drill"),
    "30.7": R("python ch30_smoke_test.py --help", edit=["ch30_service.Dockerfile"]),
}

exercises = []
SKIP = ("00_front", "20_capstones", "21_appendix")
for md in sorted(p for p in MD.glob("[0-9][0-9]*.md") if p.stem not in SKIP):
    text = md.read_text()
    chapter_title = re.search(r"^# (.+)$", text, re.M).group(1)
    for m in re.finditer(r"^:::ex (\w+) \| ([\w.]+) \| (.+?)\n(.*?)^:::$", text, re.M | re.S):
        level, ex_id, title, body = m.groups()
        lines = [l.strip() for l in body.strip().splitlines() if l.strip()]
        hint = next((l[len("**Hint:**"):].strip() for l in lines if l.startswith("**Hint:**")), None)
        done = next((l[len("**Done when:**"):].strip() for l in lines if l.startswith("**Done when:**")), None)
        task = " ".join(l for l in lines if not l.startswith(("**Hint:**", "**Done when:**")))
        entry = {"id": ex_id, "level": level, "title": title, "chapter": chapter_title,
                 "task": task, "hint": hint, "done_when": done}
        entry.update(MAP.get(ex_id, {"kind": "concept"}) if level != "Concept" else {"kind": "concept"})
        exercises.append(entry)

# Exercises that never call the model: don't warn about a missing API key.
NO_KEY = {"0.3", "0.4", "0.5", "0.6", "0.7", "18.3", "18.4", "18.5"}
for e in exercises:
    if e["id"] in NO_KEY or e["id"][0] in "PTRSA":
        e["nokey"] = True

missing = [e["id"] for e in exercises if e["level"] != "Concept" and e["id"] not in MAP]
assert not missing, missing
OUT.write_text(json.dumps(exercises, indent=1))
print(f"{len(exercises)} exercises -> {OUT}")
