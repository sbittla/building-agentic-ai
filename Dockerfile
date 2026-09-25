# Building Agentic AI course image.
# Everything needed for chapters 0-19, their solutions and the capstones:
# Python 3.12, uv, Node.js 24, the MCP SDK, reference MCP servers, MCP Inspector,
# GitHub's MCP server, sample data generators, and the `course` command.

# GitHub's official MCP server ships as a multi-arch image; we copy its binary out.
# If your network blocks ghcr.io, build with:  --build-arg GITHUB_MCP_IMAGE=nogithub
# Pin a release tag (or a digest) you have tested, e.g. ghcr.io/github/github-mcp-server:v1.2.3
ARG GITHUB_MCP_IMAGE=ghcr.io/github/github-mcp-server:latest

FROM ubuntu:24.04 AS nogithub
RUN mkdir -p /server \
 && printf '#!/bin/sh\necho "The GitHub MCP server was not included in this image build." >&2\nexit 1\n' \
      > /server/github-mcp-server && chmod +x /server/github-mcp-server

FROM ${GITHUB_MCP_IMAGE} AS githubmcp

FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    VIRTUAL_ENV=/opt/venv \
    PATH=/opt/venv/bin:/usr/local/bin:/usr/bin:/bin \
    UV_TOOL_DIR=/opt/uv-tools \
    UV_TOOL_BIN_DIR=/usr/local/bin \
    UV_PYTHON=/opt/venv/bin/python \
    NPM_CONFIG_PREFIX=/usr/local \
    HOME=/home/student \
    HF_HOME=/opt/hf \
    MODEL=claude-sonnet-5

# System packages: Python, Git, SQLite CLI, time zones, CA certificates.
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      python3.12 python3.12-venv ca-certificates git sqlite3 tzdata curl less nano \
 && rm -rf /var/lib/apt/lists/*

# Python environment for the course (one venv, used by every chapter).
RUN python3.12 -m venv /opt/venv \
 && /opt/venv/bin/pip install --no-cache-dir pip==26.2.1 uv==0.12.18
# Exact versions from requirements.lock (see requirements.in for the top-level list).
# Pinned, so the course behaves the same next year as it does today.
COPY requirements.lock /tmp/requirements.lock
RUN uv pip install --no-cache -r /tmp/requirements.lock

# The small local embedding model for chapter 17 (about 30 MB). If the download is
# blocked, chapter 17 falls back to the offline hashing embedder automatically.
RUN mkdir -p /opt/hf && (python -c "from model2vec import StaticModel; \
      StaticModel.from_pretrained('minishlab/potion-base-8M')" \
      || echo "NOTE: embedding model not downloaded; chapter 17 will use the hashing embedder") \
 && chmod -R a+rwX /opt/hf

# Node.js 24 comes from the nodejs-wheel-binaries package above (works on amd64 and arm64).
RUN NW=/opt/venv/lib/python3.12/site-packages/nodejs_wheel \
 && ln -s $NW/bin/node /usr/local/bin/node \
 && ln -s $NW/lib/node_modules/npm/bin/npm-cli.js /usr/local/bin/npm \
 && ln -s $NW/lib/node_modules/npm/bin/npx-cli.js /usr/local/bin/npx \
 && node --version && npm --version

# Node-based tools: MCP Inspector and the Filesystem and Memory reference servers.
RUN npm install -g --no-fund --no-audit \
      @modelcontextprotocol/inspector@2.8.0 \
      @modelcontextprotocol/server-filesystem@2026.8.31 \
      @modelcontextprotocol/server-memory@2026.8.31 \
 && npm cache clean --force

# Python-based reference servers: Git, Fetch, Time.
RUN uv tool install mcp-server-git==2026.8.18 \
 && uv tool install mcp-server-fetch==2026.8.18 \
 && uv tool install mcp-server-time==2026.8.18 \
 && rm -rf /home/student/.cache

# GitHub's MCP server binary.
COPY --from=githubmcp /server/github-mcp-server /usr/local/bin/github-mcp-server

# Course material: pristine code, data generators, self-tests and the course CLI.
COPY course/ /opt/course/
RUN printf '#!/bin/sh\nexec /opt/venv/bin/python /opt/course/course.py "$@"\n' > /usr/local/bin/course \
 && chmod +x /usr/local/bin/course \
 && mkdir -p /home/student /workspace \
 && chmod 777 /home/student /workspace \
 && git config --system user.name "Course Student" \
 && git config --system user.email "student@example.com" \
 && git config --system --add safe.directory '*'

WORKDIR /workspace
ENTRYPOINT ["course"]
CMD ["help"]
