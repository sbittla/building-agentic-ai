# Solutions

This folder has a worked solution for every exercise in the book and working versions of all six capstone projects. Try each exercise yourself first. You'll learn far more from getting stuck and unstuck than from reading an answer. Then compare.

## What's here

| Path | Contents |
| --- | --- |
| `exercises/` | Solutions for every hands-on exercise: `ex<id>_*.py` (for example `ex4_4_tracer.py`, `exS_3_parameters.py`), plus `sol_chNN_*.py` for exercises that extend a chapter's file |
| `capstones/` | Complete capstone projects: sample data, MCP servers, the agent and evaluation cases |
| `ANSWERS.md` | Sample answers for every concept exercise, the written parts of other exercises, and what you should see for exercises that print results |
| `tests/` | Automated checks that run every solution and capstone |
| `index.json` | Which files solve which exercise |

## Commands (from the kit folder)

```
./course.sh solution 4.4        # show the solution for exercise 4.4
./course.sh solution 8.1        # concept exercises show the sample answer
./course.sh check-solutions     # run every solution and capstone, offline
```

On Windows use `.\course.cmd` instead of `./course.sh`.

`check-solutions` needs no API key and costs nothing. It copies the original course code into a scratch folder, generates the sample data, and stands in a scripted "model" for Claude. It then runs:

- **Every solution and capstone** against the real tools, databases, files and MCP servers (the course's own plus the Filesystem, Git, Fetch, Time and Memory reference servers), and the network-less sandbox.
- **The frameworks and services of Part 6** for real: the Claude Agent SDK runtime and the SDK's tool runner against a local fake of the Messages API, LangChain with a scripted chat model, and the agent API and remote MCP server as running web servers.
- **Every `./course.sh ex <id>` command** as it ships, with a generic stand-in model.

It proves the code works: tool calls, loops, stop conditions, approval gates, error handling, MCP transports and the sandbox. It can't show how well a real model does, because the stand-in follows a script. Run a solution with your own API key to see real behavior.

## Running a solution with a real model

Solutions build on the chapter files in your workspace, so run them from there:

```
./course.sh shell
export PYTHONPATH=/solutions/exercises:$PYTHONPATH
python /solutions/exercises/ex4_4_tracer.py
```

## Running a capstone

With your API key in `.env`, from the kit folder:

```
./course.sh capstone            # list the capstones
./course.sh capstone 1          # creates the sample data, then runs the support agent
./course.sh capstone 4 pr-3     # extra arguments go to the capstone program
./course.sh capstone 5 "Should our team adopt MCP?"
```

Each capstone is described, file by file, at the end of its section in the book's capstones chapter.
