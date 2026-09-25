#!/usr/bin/env bash
# Building Agentic AI: run any course command inside Docker.
# Usage: ./course.sh help
set -euo pipefail
cd "$(dirname "$0")"

export COURSE_HOST_DIR="$(pwd)"
if [ "$(uname -s)" = "Linux" ]; then       # files the container creates stay yours
  export COURSE_UID="$(id -u)" COURSE_GID="$(id -g)"
fi
mkdir -p workspace/.sandbox
cmd="${1:-help}"

secret() { LC_ALL=C tr -dc 'A-Za-z0-9' </dev/urandom | head -c 32; }
env_has() { grep -Eq "^$1=.+" .env 2>/dev/null; }

setup() {
  echo "== Building Agentic AI: setup =="
  if ! command -v docker >/dev/null 2>&1; then
    echo "1. Docker: NOT INSTALLED. Install Docker Desktop (macOS/Windows) or Docker Engine"
    echo "   with the Compose plugin (Linux): https://docs.docker.com/get-docker/"
  elif ! docker info >/dev/null 2>&1; then
    echo "1. Docker: installed but NOT RUNNING. Start Docker Desktop (or: sudo systemctl start docker)."
  else
    echo "1. Docker: OK"
  fi
  if [ ! -f .env ]; then cp .env.example .env; echo "2. Created .env from .env.example"; else echo "2. .env: found"; fi
  choice=1
  if grep -q '^PROVIDER=local' .env; then
    choice=2; echo "3. Model: the free local model (PROVIDER=local in .env)"
  elif ! env_has ANTHROPIC_API_KEY || grep -q '^ANTHROPIC_API_KEY=sk-ant-your-key-here' .env; then
    echo "3. Which model do you want to use? (you can switch later in .env; see Appendix H)"
    echo "   1) Claude through the Claude API: best results, pay per use (about \$25-50 for the book)"
    echo "   2) qwen3.5:9b, a free open model on your own computer: needs 16 GB of RAM or more"
    read -rp "   Choose 1 or 2 [1]: " choice || choice=1
  fi
  if [ "${choice:-1}" = "2" ]; then
    if ! grep -q '^PROVIDER=local' .env; then
      grep -v '^PROVIDER=' .env > .env.tmp || true
      { echo "PROVIDER=local"; cat .env.tmp; } > .env; rm -f .env.tmp
      echo "   Saved PROVIDER=local. Start the model with:  ./course.sh local up"
    fi
  else
    if env_has ANTHROPIC_API_KEY && ! grep -q '^ANTHROPIC_API_KEY=sk-ant-your-key-here' .env; then
      echo "3. API key: already set"
    else
      echo "3. API key: paste your Anthropic API key (it starts with sk-ant-; typing is hidden)."
      echo "   Don't have one? See 'Getting an API key' in Chapter 0 of the book."
      if [[ "${ANTHROPIC_API_KEY:-}" == sk-* ]]; then
        key="$ANTHROPIC_API_KEY"; echo "   Using ANTHROPIC_API_KEY from your environment."
      else
        read -rsp "   Key: " key; echo
      fi
      case "$key" in
        sk-*) grep -v '^ANTHROPIC_API_KEY=' .env > .env.tmp || true
              { printf 'ANTHROPIC_API_KEY=%s\n' "$key"; cat .env.tmp; } > .env; rm -f .env.tmp
              echo "   Saved.";;
        *)    echo "   That doesn't look like an API key (it should start with sk-). Run setup again.";;
      esac
    fi
  fi
  for name in AGENT_API_KEYS MCP_TOKEN MCP_READONLY_TOKEN; do       # chapter 19 secrets
    if ! env_has "$name"; then printf '%s=%s\n' "$name" "$(secret)" >> .env; fi
  done
  echo "4. Chapter 19 keys: set (random, in .env)"
  chmod 600 .env 2>/dev/null || true
  echo; echo "Next:  ./course.sh build   then   ./course.sh selftest   then   ./course.sh check --api"
  if grep -q '^PROVIDER=local' .env; then
    echo "       (local model: run  ./course.sh local up  before  check --api)"
  fi
}

if [ "$cmd" = "setup" ]; then setup; exit 0; fi

if ! command -v docker >/dev/null 2>&1; then
  echo "Docker is not installed. Run ./course.sh setup for help." >&2
  exit 1
fi
if ! docker info >/dev/null 2>&1; then
  echo "Docker is not running. Start Docker Desktop (or the Docker service) and try again." >&2
  exit 1
fi
if [ "$cmd" != "build" ] && ! docker image inspect building-agentic-ai:latest >/dev/null 2>&1; then
  echo "First run: building the course image (this takes a few minutes, once)..." >&2
  docker compose build
fi

case "$cmd" in
  build)
    shift; exec docker compose build "$@" ;;
  sandbox)
    case "${2:-up}" in
      up)     exec docker compose --profile sandbox up -d sandbox ;;
      down)   exec docker compose --profile sandbox stop sandbox ;;
      logs)   exec docker compose --profile sandbox logs -f sandbox ;;
      status) exec docker compose --profile sandbox ps sandbox ;;
      *) echo "Usage: ./course.sh sandbox up|down|logs|status" >&2; exit 2 ;;
    esac ;;
  local)        # the free local model (Appendix H): up [--gpu|--native] | down | status | logs
    files="-f compose.yaml"
    case " $* " in *" --gpu "*) files="$files -f compose.gpu.yaml" ;; esac
    case "${2:-status}" in
      up)
        case " $* " in
          *" --native "*) docker compose --profile local up -d local-adapter ;;
          *)              docker compose $files --profile local up -d local-model local-adapter ;;
        esac
        docker compose run --rm course local-pull
        grep -q '^PROVIDER=local' .env 2>/dev/null \
          || echo "Now set PROVIDER=local in .env to use it, then run: ./course.sh check --api" ;;
      down)   exec docker compose --profile local stop local-model local-adapter ;;
      status) docker compose --profile local ps local-model local-adapter
              exec docker compose run --rm course local-status ;;
      logs)   exec docker compose --profile local logs -f local-model local-adapter ;;
      *) echo "Usage: ./course.sh local up [--gpu|--native] | down | status | logs" >&2; exit 2 ;;
    esac ;;
  mcp)          # stdio MCP server for Claude Desktop and other MCP hosts (no TTY!)
    shift; exec docker compose run --rm -T course "$@" ;;
  inspector|serve)
    exec docker compose run --rm --service-ports course "$@" ;;
  serve-api)    # a fixed name lets other course containers reach it; publish only its port
    exec docker compose run --rm -p 127.0.0.1:8080:8080 --name agentic-ai-api course "$@" ;;
  serve-mcp)
    exec docker compose run --rm -p 127.0.0.1:8000:8000 --name agentic-ai-mcp course "$@" ;;
  ex|exercise)
    if [[ "${2:-}" == 12.* ]]; then
      exec docker compose run --rm --service-ports course "$@"
    fi
    exec docker compose run --rm course "$@" ;;
  *)
    exec docker compose run --rm course "$@" ;;
esac
