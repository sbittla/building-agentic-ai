# Run the course free with a local model (qwen3.5:9b)

This guide sets up **`qwen3.5:9b`**, a free open-source model, in Docker on your own computer, so you can do the book's exercises without an API key and without paying for API calls. It's the same material as **Appendix H** of the book, with every command in one place. The book's code doesn't change: one line in `.env` decides whether it talks to Claude or to the local model.

On Windows, type `.\course.cmd` wherever this guide shows `./course.sh`.

## 1. Check your computer

| | Minimum | Recommended |
| --- | --- | --- |
| Memory (RAM) | 16 GB | 32 GB |
| Free disk space | 10 GB (model 6.6 GB, course image about 2 GB) | 15 GB |
| GPU | None: the CPU works, just slower | NVIDIA with 8 GB or more of video memory |
| Software | Docker Desktop (Windows, macOS) or Docker Engine with Compose (Linux) | the same |

Check Docker is installed and running:

```bash
docker version
docker compose version
```

If either fails, install Docker first (see "Setup" in *How to Use This Book*, or docs.docker.com/get-docker).

## 2. Get the course kit and build it

```bash
git clone https://github.com/sbittla/building-agentic-ai.git
cd building-agentic-ai
./course.sh setup          # choose 2 for "qwen3.5:9b, a free open model"
./course.sh build          # a few minutes, once
./course.sh selftest       # offline check: should end with 22/22 checks passed
```

Choosing **2** in `setup` writes `PROVIDER=local` into `.env`. You don't need an API key.

## 3. Start the model

```bash
./course.sh local up           # starts Ollama and downloads qwen3.5:9b (about 6.6 GB) the first time
./course.sh local up --gpu     # the same, using an NVIDIA GPU
./course.sh local status       # "Local model server running. Models: qwen3.5:9b"
./course.sh check --api        # one tiny call; the reply comes from qwen3.5:9b
```

What `local up` starts, from `compose.yaml` (profile `local`):

| Container | What it does |
| --- | --- |
| `local-model` | Ollama, the model server. The model is stored in the Docker volume `ollama-models`, so it's downloaded only once. It listens on `127.0.0.1:11434` (your machine only). |
| `local-adapter` | The course's adapter (`course/local_adapter.py`) between the book's code and Ollama: it handles forced tools, structured outputs and prompt caching, and explains clearly when an exercise needs Claude. |

`./course.sh local down` stops both and frees the memory. `./course.sh local logs` shows what they're doing.

## 4. Do the exercises

Nothing changes: `./course.sh ex 4.2`, `./course.sh python ch04_agent.py`, `./course.sh ask ch08_sql_tools` and the rest all use the local model while `PROVIDER=local` is set.

Every exercise is labelled with the model it needs, in the book's exercise boxes, in `./course.sh list` and in `./course.sh ex <id> --info`:

| Label | Count | What it means |
| --- | --- | --- |
| No model | 81 | Nothing calls a model: free with either choice |
| qwen3.5:9b or Claude | 83 | Runs on the local model or on Claude |
| Claude recommended | 4 | 16.5, 24.4, 24.5, 24.7: runs locally, but much better on Claude |
| Claude only | 5 | 3.8, 12.5, 16.8, 24.8, 24.9: needs Claude (12.5 uses the Claude Desktop app) |

The full list, exercise by exercise, is in `course/model_needs.json` and in Appendix H of the book.

## 5. Check everything at once

```bash
./course.sh live-check --yes                 # every chapter's main file (25 programs)
./course.sh live-check exercises --yes       # every exercise that uses a model, with its reference solution
./course.sh live-check exercises 4 --yes     # just Chapter 4's exercises
./course.sh check-solutions                  # all solutions offline, with a stand-in model (no model needed)
```

The two `live-check` commands write `workspace/live_report.md` and `workspace/live_exercises_report.md`. **PASS** means the program ran without errors. Read the answers to judge their quality: a 9B model makes more mistakes than Claude. On a CPU, allow an hour for `live-check` and several hours for `live-check exercises`.

## 6. Switch between Claude and the local model

| `.env` | Model used |
| --- | --- |
| `PROVIDER=local` | `qwen3.5:9b` on your computer |
| `PROVIDER=claude`, or no `PROVIDER` line | Claude, with your `ANTHROPIC_API_KEY` |

Optional settings for `.env`:

| Setting | Default | What it does |
| --- | --- | --- |
| `LOCAL_MODEL` | `qwen3.5:9b` | The Ollama model to use |
| `LOCAL_CONTEXT` | `32768` | Context window in tokens; `16384` uses less memory |
| `LOCAL_THINKING` | `auto` | `off` skips the reasoning step: much faster on a CPU, a little less accurate |
| `OLLAMA_URL` | the `local-model` container | Only for Ollama running as an app on your computer (below) |

## 7. Platform notes

**Windows.** Docker Desktop runs containers inside WSL 2, which usually gets about half of your RAM. That's enough for `qwen3.5:9b`. If the model stops with an out-of-memory error, create `C:\Users\<you>\.wslconfig` with:

```
[wsl2]
memory=12GB
```

Then run `wsl --shutdown` in PowerShell and restart Docker Desktop. For an NVIDIA GPU, install the current NVIDIA driver and use `.\course.cmd local up --gpu`.

**macOS.** Docker can't use a Mac's GPU. On Apple Silicon it's much faster to run Ollama as a normal app:

1. Install Ollama from ollama.com, run `ollama pull qwen3.5:9b`, and set the context length to 32k in Ollama's settings.
2. In `.env`: `PROVIDER=local` and `OLLAMA_URL=http://host.docker.internal:11434`.
3. `./course.sh local up --native` (starts only the adapter).

**Linux.** Nothing extra. For an NVIDIA GPU, install the NVIDIA Container Toolkit, then `./course.sh local up --gpu`.

## 8. Troubleshooting

| Symptom | Fix |
| --- | --- |
| "Can't reach the local model" | `./course.sh local up`, then `./course.sh local status` |
| "The model 'qwen3.5:9b' isn't downloaded yet" | `./course.sh local up` again; it resumes the download |
| The download fails or stalls | Check your connection and run `./course.sh local up` again. Behind a company proxy, Docker Desktop's proxy settings must allow `registry.ollama.ai`. |
| Out of memory, or the model container restarts | Close other programs, set `LOCAL_CONTEXT=16384`, or give WSL more memory (above) |
| Very slow | Use `--gpu`, set `LOCAL_THINKING=off`, run evals with one trial, and use fewer users in load tests (29.2, 30.7) |
| "The local model didn't call … correctly after 3 tries" | Run it again, make the tool description clearer (Chapter 3), or use Claude for that run |
| "… needs Claude, not the local model" | The exercise is **Claude only**: set `PROVIDER=claude` for it |
| Port 11434 already in use | Ollama already runs as an app: quit it, or use it with `OLLAMA_URL` and `local up --native` |
| `--gpu` fails | Update the NVIDIA driver (Windows) or install the NVIDIA Container Toolkit (Linux). `./course.sh local logs` shows whether Ollama found the GPU |
| 8 GB GPU: the model loads partly on the CPU, or fails with "cudaMalloc failed: out of memory" | Set `LOCAL_CONTEXT=8192` in `.env`. The weights and a 32K context don't both fit in 8 GB; `compose.gpu.yaml` already keeps 2 GB free and halves the context cache |
| Windows + GPU: every Docker container restarts when the model loads, and runs end with `error waiting for container: unexpected EOF` | WSL's GPU driver is in a bad state. Run `wsl --shutdown` in PowerShell (Docker Desktop restarts itself), then `.\course.cmd local up --gpu`. If it keeps happening, reboot, or use the CPU (`local up` without `--gpu`) |
| A long exercise times out (7.6, 24.5, 27.3) | The course allows each model call 600 s on the local model (`MODEL_TIMEOUT` in `.env` changes it) and each exercise 30 minutes. Use `--gpu`, `LOCAL_THINKING=off`, or run that exercise on Claude |

## 9. Remove it

```bash
./course.sh local down
docker volume rm building-agentic-ai_ollama-models   # deletes the downloaded model (6.6 GB)
```

Then delete the `PROVIDER=local` line from `.env`.
