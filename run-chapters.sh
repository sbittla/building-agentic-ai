#!/usr/bin/env bash
# Building Agentic AI Systems: run every chapter's exercises and keep their output.
#   ./run-chapters.sh                    every chapter, free local model (qwen3.5:9b)
#   ./run-chapters.sh 7                  just chapter 7
#   ./run-chapters.sh 7 --model claude   chapter 7 with Claude (needs your API key in .env)
#   ./run-chapters.sh all --free-only    only the exercises that need no model
# The logs go to solutions/outputs (open solutions/outputs/README.md).
set -uo pipefail
cd "$(dirname "$0")"

args=("$@")
if [ ${#args[@]} -eq 0 ]; then
  args=(all)
elif [[ "${args[0]}" == -* ]]; then
  args=(all "${args[@]}")
fi

# The local model must be running (it downloads about 6.6 GB the first time), unless
# you chose Claude or only the free exercises.
need_local=1
[ "${RUN_MODEL:-}" = "claude" ] && need_local=0
case " ${args[*]} " in
  *" --model claude "*|*" --model=claude "*|*" --free-only "*) need_local=0 ;;
esac
if [ "$need_local" = 1 ]; then
  echo "Starting the free local model first: ./course.sh local up"
  ./course.sh local up
fi

./course.sh run-chapter "${args[@]}" --yes
status=$?
echo
echo "Finished. The output of every exercise is in solutions/outputs;"
echo "open solutions/outputs/README.md for the overview."
exit $status
