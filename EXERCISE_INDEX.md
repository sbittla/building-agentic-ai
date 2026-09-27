# Complete Exercise Index

**Building Agentic AI Systems**  
Quick reference for all exercises, organized by chapter with file locations and how to run them.

---

## Quick Navigation

- **[Chapter 0: Agentic Foundations](#chapter-0-agentic-foundations)** — 4 exercises
- **[Chapter 1: The Agent Loop](#chapter-1-the-agent-loop)** — 5 exercises  
- **[Chapter 2: Building with Claude](#chapter-2-building-with-claude)** — 3 exercises
- **[Chapter 3: Tool Use & Actions](#chapter-3-tool-use--actions)** — 5 exercises
- **[Chapter 4: Agentic Loops at Scale](#chapter-4-agentic-loops-at-scale)** — 4 exercises
- **[Chapter 5: State and Short-Term Memory](#chapter-5-state-and-short-term-memory)** — 3 exercises
- **[Interludes](#interludes)** — Python, SQL, Regex, Testing
- **[Capstone Projects](#capstone-projects)** — 6 major projects

---

## Chapter 0: Agentic Foundations

**Learning Level:** Beginner  
**Topics:** What agents are, autonomy vs automation, agent spectrum

### 0.1 — Intro to Agents
- **File:** `solutions/exercises/ch00/ex0_1_intro.py`
- **Or (direct access):** `solutions/exercises/_index/ex0_1_intro.py`
- **Run:** `./course.sh solution 0.1`
- **Output:** `solutions/outputs/ch00/ex0_1.log`
- **Description:** Understand what agents are and when to build them

### 0.2 — Agent vs Workflow
- **File:** `solutions/exercises/ch00/ex0_2_comparison.py`
- **Or (direct):** `solutions/exercises/_index/ex0_2_comparison.py`
- **Run:** `./course.sh solution 0.2`
- **Output:** `solutions/outputs/ch00/ex0_2.log`
- **Description:** Compare autonomous agents vs workflow automation

### 0.3 — First Loop
- **File:** `solutions/exercises/ch00/ex0_3_loop.py`
- **Or (direct):** `solutions/exercises/_index/ex0_3_loop.py`
- **Run:** `./course.sh solution 0.3`
- **Output:** `solutions/outputs/ch00/ex0_3.log`
- **Description:** Build your first agent loop

### 0.4 — Agent Basics
- **File:** `solutions/exercises/ch00/ex0_4_basics.py`
- **Or (direct):** `solutions/exercises/_index/ex0_4_basics.py`
- **Run:** `./course.sh solution 0.4`
- **Output:** `solutions/outputs/ch00/ex0_4.log`
- **Description:** Core agent patterns and initialization

---

## Chapter 1: The Agent Loop

**Learning Level:** Intermediate  
**Topics:** Turn-taking, loop architecture, termination conditions

### 1.1 — Loop Anatomy
- **File:** `solutions/exercises/ch01/ex1_1_anatomy.py`
- **Or (direct):** `solutions/exercises/_index/ex1_1_anatomy.py`
- **Run:** `./course.sh solution 1.1`
- **Output:** `solutions/outputs/ch01/ex1_1.log`
- **Description:** Dissect and understand the agent loop structure

### 1.2 — Turn Taking
- **File:** `solutions/exercises/ch01/ex1_2_turns.py`
- **Or (direct):** `solutions/exercises/_index/ex1_2_turns.py`
- **Run:** `./course.sh solution 1.2`
- **Output:** `solutions/outputs/ch01/ex1_2.log`
- **Description:** Implement multi-turn conversation handling

### 1.3 — Workflow Design
- **File:** `solutions/exercises/ch01/ex1_3_workflow.py`
- **Or (direct):** `solutions/exercises/_index/ex1_3_workflow.py`
- **Run:** `./course.sh solution 1.3`
- **Output:** `solutions/outputs/ch01/ex1_3.log`
- **Description:** Design effective agent workflows

### 1.4 — Termination
- **File:** `solutions/exercises/ch01/ex1_4_termination.py`
- **Or (direct):** `solutions/exercises/_index/ex1_4_termination.py`
- **Run:** `./course.sh solution 1.4`
- **Output:** `solutions/outputs/ch01/ex1_4.log`
- **Description:** Add stopping conditions and graceful exits

### 1.5 — Routing Decisions
- **File:** `solutions/exercises/ch01/ex1_5_routing.py`
- **Or (direct):** `solutions/exercises/_index/ex1_5_routing.py`
- **Run:** `./course.sh solution 1.5`
- **Output:** `solutions/outputs/ch01/ex1_5.log`
- **Description:** Route decisions based on agent state

---

## Chapter 2: Building with Claude

**Learning Level:** Intermediate  
**Topics:** Claude API, streaming, function calling

### 2.1 — Basic API Call
- **File:** `solutions/exercises/ch02/ex2_1_api.py`
- **Or (direct):** `solutions/exercises/_index/ex2_1_api.py`
- **Run:** `./course.sh solution 2.1`
- **Output:** `solutions/outputs/ch02/ex2_1.log`
- **Description:** Make your first Claude API call

### 2.2 — Streaming
- **File:** `solutions/exercises/ch02/ex2_2_streaming.py`
- **Or (direct):** `solutions/exercises/_index/ex2_2_streaming.py`
- **Run:** `./course.sh solution 2.2`
- **Output:** `solutions/outputs/ch02/ex2_2.log`
- **Description:** Handle streaming responses from Claude

### 2.3 — Tool Use
- **File:** `solutions/exercises/ch02/ex2_3_tools.py`
- **Or (direct):** `solutions/exercises/_index/ex2_3_tools.py`
- **Run:** `./course.sh solution 2.3`
- **Output:** `solutions/outputs/ch02/ex2_3.log`
- **Description:** Use Claude's function calling for tool invocation

---

## Chapter 3: Tool Use & Actions

**Learning Level:** Intermediate  
**Topics:** Tool definition, tool results, approval workflows, routing

### 3.1 — Tool Definition
- **File:** `solutions/exercises/ch03/ex3_1_define.py`
- **Or (direct):** `solutions/exercises/_index/ex3_1_define.py`
- **Run:** `./course.sh solution 3.1`
- **Output:** `solutions/outputs/ch03/ex3_1.log`
- **Description:** Define tools for your agent to use

### 3.2 — Tool Results
- **File:** `solutions/exercises/ch03/ex3_2_results.py`
- **Or (direct):** `solutions/exercises/_index/ex3_2_results.py`
- **Run:** `./course.sh solution 3.2`
- **Output:** `solutions/outputs/ch03/ex3_2.log`
- **Description:** Process and handle tool execution results

### 3.3 — Error Handling
- **File:** `solutions/exercises/ch03/ex3_3_errors.py`
- **Or (direct):** `solutions/exercises/_index/ex3_3_errors.py`
- **Run:** `./course.sh solution 3.3`
- **Output:** `solutions/outputs/ch03/ex3_3.log`
- **Description:** Handle tool errors gracefully

### 3.4 — Approval Workflows
- **File:** `solutions/exercises/ch03/ex3_4_approval.py`
- **Or (direct):** `solutions/exercises/_index/ex3_4_approval.py`
- **Run:** `./course.sh solution 3.4`
- **Output:** `solutions/outputs/ch03/ex3_4.log`
- **Description:** Require approval before tool execution

### 3.5 — Routing Logic
- **File:** `solutions/exercises/ch03/ex3_5_routing.py`
- **Or (direct):** `solutions/exercises/_index/ex3_5_routing.py`
- **Run:** `./course.sh solution 3.5`
- **Output:** `solutions/outputs/ch03/ex3_5.log`
- **Description:** Route to different tools based on context

---

## Chapter 4: Agentic Loops at Scale

**Learning Level:** Advanced  
**Topics:** Cost tracking, iteration limits, debugging

### 4.1 — Cost Tracking
- **File:** `solutions/exercises/ch04/ex4_1_cost.py`
- **Or (direct):** `solutions/exercises/_index/ex4_1_cost.py`
- **Run:** `./course.sh solution 4.1`
- **Output:** `solutions/outputs/ch04/ex4_1.log`
- **Description:** Track computational costs in agent loops

### 4.2 — Loop Limits
- **File:** `solutions/exercises/ch04/ex4_2_limits.py`
- **Or (direct):** `solutions/exercises/_index/ex4_2_limits.py`
- **Run:** `./course.sh solution 4.2`
- **Output:** `solutions/outputs/ch04/ex4_2.log`
- **Description:** Add iteration caps and stopping conditions

### 4.3 — Silent Failures
- **File:** `solutions/exercises/ch04/ex4_3_failures.py`
- **Or (direct):** `solutions/exercises/_index/ex4_3_failures.py`
- **Run:** `./course.sh solution 4.3`
- **Output:** `solutions/outputs/ch04/ex4_3.log`
- **Description:** Debug and prevent runaway loops

### 4.4 — Tracer & Debug
- **File:** `solutions/exercises/ch04/ex4_4_tracer.py`
- **Or (direct):** `solutions/exercises/_index/ex4_4_tracer.py`
- **Run:** `./course.sh solution 4.4`
- **Output:** `solutions/outputs/ch04/ex4_4.log`
- **Description:** Use tracers for detailed debugging

---

## Chapter 5: State and Short-Term Memory

**Learning Level:** Intermediate  
**Topics:** Agent state, conversation history, episode boundaries

### 5.1 — Basic State
- **File:** `solutions/exercises/ch05/ex5_1_state.py`
- **Or (direct):** `solutions/exercises/_index/ex5_1_state.py`
- **Run:** `./course.sh solution 5.1`
- **Output:** `solutions/outputs/ch05/ex5_1.log`
- **Description:** Maintain state across agent turns

### 5.2 — Conversation History
- **File:** `solutions/exercises/ch05/ex5_2_history.py`
- **Or (direct):** `solutions/exercises/_index/ex5_2_history.py`
- **Run:** `./course.sh solution 5.2`
- **Output:** `solutions/outputs/ch05/ex5_2.log`
- **Description:** Manage conversation history in agents

### 5.3 — Episode Boundaries
- **File:** `solutions/exercises/ch05/ex5_3_episodes.py`
- **Or (direct):** `solutions/exercises/_index/ex5_3_episodes.py`
- **Run:** `./course.sh solution 5.3`
- **Output:** `solutions/outputs/ch05/ex5_3.log`
- **Description:** Define episode boundaries for memory management

---

## Interludes

Foundational skills needed across multiple chapters.

### Python Fundamentals

#### P.1 — Functions
- **File:** `solutions/exercises/interlude_python/exP_1_functions.py`
- **Or (direct):** `solutions/exercises/_index/exP_1_functions.py`
- **Run:** `./course.sh solution P.1`
- **Output:** `solutions/outputs/interlude_python/exP_1.log`

#### P.2 — Classes & Objects
- **File:** `solutions/exercises/interlude_python/exP_2_classes.py`
- **Or (direct):** `solutions/exercises/_index/exP_2_classes.py`
- **Run:** `./course.sh solution P.2`
- **Output:** `solutions/outputs/interlude_python/exP_2.log`

#### P.3 — Decorators
- **File:** `solutions/exercises/interlude_python/exP_3_decorators.py`
- **Or (direct):** `solutions/exercises/_index/exP_3_decorators.py`
- **Run:** `./course.sh solution P.3`
- **Output:** `solutions/outputs/interlude_python/exP_3.log`

#### P.4 — Async/Await
- **File:** `solutions/exercises/interlude_python/exP_4_async.py`
- **Or (direct):** `solutions/exercises/_index/exP_4_async.py`
- **Run:** `./course.sh solution P.4`
- **Output:** `solutions/outputs/interlude_python/exP_4.log`

#### P.5 — Error Handling
- **File:** `solutions/exercises/interlude_python/exP_5_errors.py`
- **Or (direct):** `solutions/exercises/_index/exP_5_errors.py`
- **Run:** `./course.sh solution P.5`
- **Output:** `solutions/outputs/interlude_python/exP_5.log`

### SQL for Agents

#### S.1 — SELECT Queries
- **File:** `solutions/exercises/interlude_sql/exS_1_select.py`
- **Or (direct):** `solutions/exercises/_index/exS_1_select.py`
- **Run:** `./course.sh solution S.1`
- **Output:** `solutions/outputs/interlude_sql/exS_1.log`

#### S.2 — Joins & Aggregates
- **File:** `solutions/exercises/interlude_sql/exS_2_joins.py`
- **Or (direct):** `solutions/exercises/_index/exS_2_joins.py`
- **Run:** `./course.sh solution S.2`
- **Output:** `solutions/outputs/interlude_sql/exS_2.log`

#### S.3 — Transactions
- **File:** `solutions/exercises/interlude_sql/exS_3_transactions.py`
- **Or (direct):** `solutions/exercises/_index/exS_3_transactions.py`
- **Run:** `./course.sh solution S.3`
- **Output:** `solutions/outputs/interlude_sql/exS_3.log`

#### S.4 — Injection Attacks
- **File:** `solutions/exercises/interlude_sql/exS_4_injection.py`
- **Or (direct):** `solutions/exercises/_index/exS_4_injection.py`
- **Run:** `./course.sh solution S.4`
- **Output:** `solutions/outputs/interlude_sql/exS_4.log`

### Regex for Parsing

#### R.1 — Pattern Basics
- **File:** `solutions/exercises/interlude_regex/exR_1_basics.py`
- **Or (direct):** `solutions/exercises/_index/exR_1_basics.py`
- **Run:** `./course.sh solution R.1`
- **Output:** `solutions/outputs/interlude_regex/exR_1.log`

#### R.2 — Capture Groups
- **File:** `solutions/exercises/interlude_regex/exR_2_capture.py`
- **Or (direct):** `solutions/exercises/_index/exR_2_capture.py`
- **Run:** `./course.sh solution R.2`
- **Output:** `solutions/outputs/interlude_regex/exR_2.log`

#### R.3 — Named Groups
- **File:** `solutions/exercises/interlude_regex/exR_3_named.py`
- **Or (direct):** `solutions/exercises/_index/exR_3_named.py`
- **Run:** `./course.sh solution R.3`
- **Output:** `solutions/outputs/interlude_regex/exR_3.log`

#### R.4 — Real-World Parsing
- **File:** `solutions/exercises/interlude_regex/exR_4_parsing.py`
- **Or (direct):** `solutions/exercises/_index/exR_4_parsing.py`
- **Run:** `./course.sh solution R.4`
- **Output:** `solutions/outputs/interlude_regex/exR_4.log`

### Testing Agents

#### T.1 — Unit Testing
- **File:** `solutions/exercises/interlude_testing/exT_1_unit.py`
- **Or (direct):** `solutions/exercises/_index/exT_1_unit.py`
- **Run:** `./course.sh solution T.1`
- **Output:** `solutions/outputs/interlude_testing/exT_1.log`

#### T.2 — Mocking Tools
- **File:** `solutions/exercises/interlude_testing/exT_2_mocking.py`
- **Or (direct):** `solutions/exercises/_index/exT_2_mocking.py`
- **Run:** `./course.sh solution T.2`
- **Output:** `solutions/outputs/interlude_testing/exT_2.log`

#### T.3 — Integration Tests
- **File:** `solutions/exercises/interlude_testing/exT_3_integration.py`
- **Or (direct):** `solutions/exercises/_index/exT_3_integration.py`
- **Run:** `./course.sh solution T.3`
- **Output:** `solutions/outputs/interlude_testing/exT_3.log`

#### T.4 — Property-Based Testing
- **File:** `solutions/exercises/interlude_testing/exT_4_properties.py`
- **Or (direct):** `solutions/exercises/_index/exT_4_properties.py`
- **Run:** `./course.sh solution T.4`
- **Output:** `solutions/outputs/interlude_testing/exT_4.log`

#### T.5 — Benchmarking
- **File:** `solutions/exercises/interlude_testing/exT_5_benchmarking.py`
- **Or (direct):** `solutions/exercises/_index/exT_5_benchmarking.py`
- **Run:** `./course.sh solution T.5`
- **Output:** `solutions/outputs/interlude_testing/exT_5.log`

---

## Capstone Projects

Real-world projects that integrate multiple chapters.

### C1 — Support Agent
**Estimated Time:** 6 hours  
**Topics:** Multi-turn support, tool use, state management

- **Files:** `solutions/exercises/capstones/exA_1_support/`
- **Or (direct):** `solutions/exercises/_index/exA_1_support.py`
- **Run:** `./course.sh solution A.1`
- **Output:** `solutions/outputs/capstones/exA_1.log`
- **Description:** Build a multi-turn support ticket resolver

### C2 — Data Analyst
**Estimated Time:** 8 hours  
**Topics:** SQL integration, RAG, structured output

- **Files:** `solutions/exercises/capstones/exA_2_analyst/`
- **Or (direct):** `solutions/exercises/_index/exA_2_analyst.py`
- **Run:** `./course.sh solution A.2`
- **Output:** `solutions/outputs/capstones/exA_2.log`
- **Description:** Create an agent that analyzes business data

### C3 — Code Generator
**Estimated Time:** 10 hours  
**Topics:** Code generation, debugging, iteration

- **Files:** `solutions/exercises/capstones/exA_3_codegen/`
- **Or (direct):** `solutions/exercises/_index/exA_3_codegen.py`
- **Run:** `./course.sh solution A.3`
- **Output:** `solutions/outputs/capstones/exA_3.log`
- **Description:** Build an agent that creates and debugs code

### C4 — Researcher
**Estimated Time:** 8 hours  
**Topics:** Information gathering, synthesis, citations

- **Files:** `solutions/exercises/capstones/exA_4_researcher/`
- **Or (direct):** `solutions/exercises/_index/exA_4_researcher.py`
- **Run:** `./course.sh solution A.4`
- **Output:** `solutions/outputs/capstones/exA_4.log`
- **Description:** Implement research and synthesis capabilities

### C5 — Product Manager
**Estimated Time:** 12 hours  
**Topics:** Requirements, planning, implementation

- **Files:** `solutions/exercises/capstones/exA_5_pm/`
- **Or (direct):** `solutions/exercises/_index/exA_5_pm.py`
- **Run:** `./course.sh solution A.5`
- **Output:** `solutions/outputs/capstones/exA_5.log`
- **Description:** Turn requirements into implementation plans

### C6 — Production System
**Estimated Time:** 15 hours  
**Topics:** Deployment, isolation, monitoring

- **Files:** `solutions/exercises/capstones/exA_6_production/`
- **Or (direct):** `solutions/exercises/_index/exA_6_production.py`
- **Run:** `./course.sh solution A.6`
- **Output:** `solutions/outputs/capstones/exA_6.log`
- **Description:** Deploy an agent safely to production

---

## Code Modules Reference

All code used by exercises, organized by chapter.

### Chapter 0 Code Modules
- **ch00_http.py** — HTTP utilities for API calls
- **ch00_json.py** — JSON parsing and generation
- **ch00_python_tour.py** — Python feature overview

### Chapter 1 Code Modules
- **ch01_routing.py** — Routing logic and patterns
- **ch01_summarize.py** — Text summarization utilities

### Chapter 3 Code Modules
- **ch03_tools.py** — Tool definition helpers
- **ch03_routing_eval.py** — Routing evaluation

### Chapter 4 Code Modules
- **ch04_agent.py** — Basic agent loop implementation
- **ch04_tracer.py** — Execution tracing tools

**And more...** Check `course/code/_index/` for complete code module list, or `course/code/chNN/` for chapter-specific modules.

---

## How to Use This Index

### For Students
1. Find your exercise above
2. Copy the "Run" command
3. Paste into terminal
4. Check "Output" to find logs

### For Instructors
1. Link students to this file
2. Assign exercises by chapter number (e.g., "Complete 1.1-1.5")
3. Or assign by learning path
4. Check outputs in `solutions/outputs/chNN/`

### For IDEs
- **VS Code Ctrl+P:** Search `ex0_1` finds both:
  - `solutions/exercises/ch00/ex0_1_intro.py` (chapter structure)
  - `solutions/exercises/_index/ex0_1_intro.py` (direct access)
- Choose whichever is easier for you

### File Location Cheat Sheet

| What | Where | Direct Path |
|-----|-------|-------------|
| Exercise | `solutions/exercises/chNN/exN_M_name.py` | `solutions/exercises/_index/exN_M_name.py` |
| Code module | `course/code/chNN/chNN_name.py` | `course/code/_index/chNN_name.py` |
| Output log | `solutions/outputs/chNN/exN_M.log` | Same |
| Solution | `solutions/exercises/chNN/sol_chNN_name.py` | `solutions/exercises/_index/sol_chNN_name.py` |

---

## Navigation Tips

**Ctrl+F to Search:**
- Find chapter: `## Chapter 3`
- Find exercise: `### 3.5`
- Find by name: `Routing Logic`
- Find code: `ch00_http.py`

**Click to Jump:**
- Use the Quick Navigation at the top
- Jump back to top with links

---

**Total Exercises:** 130+  
**Total Code Modules:** 72+  
**Solution Files:** 15+  
**Capstone Projects:** 6  
**Last Updated:** September 27, 2026
