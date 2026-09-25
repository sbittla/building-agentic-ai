#!/usr/bin/env bash
# Re-resolve requirements.in into requirements.lock with the course image's uv.
# Afterwards: ./course.sh build, ./course.sh selftest, ./course.sh check-solutions.
set -euo pipefail
cd "$(dirname "$0")/.."
docker run --rm -v "$PWD:/k" -w /k --entrypoint uv building-agentic-ai:latest \
  pip compile --python-version 3.12 --python-platform linux requirements.in -o requirements.lock --no-header --upgrade
echo "requirements.lock updated. Rebuild and run the checks before committing it."
