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
    "P.3": B("exP_3_sorting"),
    "P.4": B("exP_4_tasklist"),
    "P.5": B("exP_5_decorators"),
    "P.6": B("exP_6_bugs"),
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
    "2.4": R("python ch02_calculator_agent.py", edit=["ch02_calculator_agent.py"]),
    "2.5": B("ex2_5_description_eval"),
    "2.6": T("test_ex2_6_errors", edit=["ch02_calculator_agent.py"]),
    "2.7": B("ex2_7_two_tools"),
    "3.3": A("ch03_tools", "What day is it? And how many km is 26.2 miles?"),
    "3.4": A("ch03_tools", "What time is it in Tokyo?", edit=["ch03_tools.py"]),
    "3.5": R("python ch03_routing_eval.py", edit=["ch03_routing_eval.py"]),
    "3.6": B("ex3_6_forced_tool"),
    "3.7": R("python ch03_routing_eval.py", edit=["ch03_tools.py", "ch03_routing_eval.py"]),
    "3.8": R("python ch03_tool_search.py"),
    "4.3": R("python ch04_agent.py"),
    "4.4": B("ex4_4_cap"),
    "4.5": B("ex4_5_tracer"),
    "4.6": B("ex4_6_chat"),
    "4.7": B("ex4_7_cost_profile"),
    "5.3": R("python ch05_todo_tools.py"),
    "5.4": R("python ch05_todo_tools.py", edit=["ch05_todo_tools.py"]),
    "5.5": R("python ch05_todo_tools.py", edit=["ch05_todo_tools.py"]),
    "5.6": R("python ch05_todo_tools.py"),
    "5.7": T("test_ex5_7_sqlite", edit=["ch05_todo_tools.py"]),
    "6.3": A("ch06_notes_tools"),
    "6.4": T("test_ex6_4_sandbox"),
    "6.5": B("ex6_5_citation_checker"),
    "6.6": A("ch06_notes_tools", "What did I write about Kafka in July 2026?", edit=["ch06_notes_tools.py"]),
    "6.7": B("ex6_7_scale_test", setup="course data notes --count 2000 --out notes_big"),
    "7.3": A("ch07_weather_tools"),
    "7.4": A("ch07_weather_tools", "Pack for Austin, and give temperatures in Fahrenheit", edit=["ch07_weather_tools.py"]),
    "7.5": A("ch07_weather_tools", edit=["ch07_weather_tools.py"]),
    "7.6": B("ex7_6_parallel"),
    "7.7": B("ex7_7_trip_benchmark"),
    "8.3": R("python ch08_sql_tools.py"),
    "8.4": A("ch08_sql_tools", edit=["ch08_sql_tools.py"]),
    "8.5": A("ch08_sql_tools", edit=["ch08_sql_tools.py"]),
    "8.6": A("ch08_sql_tools", edit=["ch08_sql_tools.py"]),
    "8.7": B("ex8_7_eval_harness"),
    "9.3": R("python ch09_organizer.py", setup="course data messy --count 15"),
    "9.4": R("python ch09_organizer.py"),
    "9.5": R("python ch09_organizer.py", edit=["ch09_organizer.py"]),
    "9.6": A("ch09_organizer", "Sort my photos by month", edit=["ch09_organizer.py"]),
    "9.7": T("test_ex9_7_policy", setup="course data messy --count 200 --out messy_big"),
    "10.3": R("python ch10_fixer.py", setup="course data repo --fresh"),
    "10.4": R("python ch10_fixer.py", setup="course data repo --fresh", edit=["ch10_fixer.py"]),
    "10.5": R("python ch10_fixer.py", edit=["ch10_fixer.py"]),
    "10.6": R("python ch10_fixer.py", setup="course data repo --fresh", edit=["ch10_fixer.py"]),
    "10.7": B("ex10_7_benchmark", needs="sandbox"),
    "11.3": R("python ch11_research_team.py"),
    "11.4": R("python ch11_research_team.py", edit=["ch11_research_team.py"]),
    "11.5": R("python ch11_research_team.py", edit=["ch11_research_team.py"]),
    "11.6": R("python ch11_research_team.py", edit=["ch11_research_team.py"]),
    "11.7": B("ex11_7_compare"),
    "11.8": R("python ch11_patterns.py"),
    "12.3": {"kind": "inspector", "server": "ch12_weather_server.py"},
    "12.4": {"kind": "inspector", "server": "ch12_weather_server.py", "edit": ["ch12_weather_server.py"]},
    "12.5": {"kind": "desktop", "server": "ch12_weather_server.py"},
    "12.6": {"kind": "inspector", "server": "exercises/ex12_6_calc_server.py", "stub": True},
    "12.7": T("test_ex12_7_http"),
    "13.3": B("ex13_3_client"),
    "13.4": R("python ch13_mcp_agent.py servers.json"),
    "13.5": R("python ch13_mcp_agent.py servers.json", edit=["ch13_mcp_agent.py"]),
    "13.6": R("python ch13_mcp_agent.py servers.json", edit=["servers.json"]),
    "13.7": R("python ch13_mcp_agent.py servers.json", edit=["ch13_mcp_agent.py"]),
    "13.8": B("ex13_8_host"),
    "13.9": B("ex13_9_coordinator"),
    "14.3": R("python ch14_policy_agent.py servers_ecosystem.json"),
    "14.4": R("python ch14_policy_agent.py servers_github.json", needs="github"),
    "14.5": R("python ch14_policy_agent.py servers_github.json", needs="github"),
    "14.6": R("python ch14_policy_agent.py servers_ecosystem.json", edit=["ch13_mcp_agent.py"]),
    "14.7": B("ex14_7_redteam"),
    "15.3": R("python ch15_eval.py eval_sql.jsonl 3", edit=["eval_sql.jsonl"]),
    "15.4": R("python ch15_loadtest.py 4 && python ch15_loadtest.py 8 && python ch15_loadtest.py 12",
              edit=["ch15_loadtest.py"]),
    "15.5": B("ex15_5_ci_gate"),
    "15.6": B("ex15_6_trace_report"),
    "15.7": B("ex15_7_real_loadtest"),
    "15.8": B("ex15_8_calibrate"),
    # ---- Part 6
    "16.3": R("python ch16_context.py", edit=["ch16_context.py"]),
    "16.4": R("python ch16_memory.py"),
    "16.5": B("ex16_5_cache_savings"),
    "16.6": T("test_ex16_6_trimming", edit=["ch16_context.py"]),
    "16.7": B("ex16_7_assistant"),
    "16.8": R("python ch16_programmatic.py"),
    "17.3": R("python ch17_rag.py search temperature units && python ch17_rag.py search ERR-4471"),
    "17.4": R("EMBEDDER=hashing python ch17_rag.py eval && EMBEDDER=local python ch17_rag.py eval"),
    "17.5": B("ex17_5_paraphrased"),
    "17.6": B("ex17_6_semantic_memory"),
    "17.7": B("ex17_7_knowledge_agent"),
    "18.3": R("python ch18_tool_runner.py", edit=["ch18_tool_runner.py"]),
    "18.4": R("python ch18_agent_sdk.py Delete all cancelled orders."),
    "18.5": B("ex18_5_sdk_mcp"),
    "18.6": B("ex18_6_langchain_approval"),
    "18.7": B("ex18_7_three_ways"),
    "18.8": R("python ch18_skills.py"),
    "18.9": R("python ch18_managed_agent.py"),
    "19.3": R("python ch19_client.py && python ch19_client.py stream"),
    "19.4": R("python ch19_client.py limits"),
    "19.5": R("python ch19_client.py words", edit=["ch19_service.py", "ch19_client.py"]),
    "19.6": B("ex19_6_remote_hub"),
    "19.7": B("ex19_7_drill"),
    "19.8": R("python ch19_smoke_test.py --help", edit=["ch19_service.Dockerfile"]),
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
NO_KEY = {"0.3", "0.4", "0.5", "0.6", "0.7", "17.3", "17.4", "17.5", "17.6"}
for e in exercises:
    if e["id"] in NO_KEY or e["id"][0] in "PTRSA":
        e["nokey"] = True

missing = [e["id"] for e in exercises if e["level"] != "Concept" and e["id"] not in MAP]
assert not missing, missing
OUT.write_text(json.dumps(exercises, indent=1))
print(f"{len(exercises)} exercises -> {OUT}")
