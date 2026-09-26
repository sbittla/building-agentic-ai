# Chapter 30: a production image for the agent API. Only the service's own code goes
# in: no course tools, no test data you don't need, no secrets.
# Build (from your workspace folder, on your computer):
#   docker build -f ch30_service.Dockerfile -t agent-api:1 .
# Any image with Python 3.12 works; slim images are small and have few packages
# to patch.
ARG BASE=python:3.12-slim
FROM ${BASE}

# Don't run as root, don't write .pyc files, log straight to stdout (the platform
# collects it).
RUN useradd --create-home --uid 10001 app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PORT=8080 \
    AGENT_SESSIONS_DB=/data/sessions.db
WORKDIR /app

# Exact versions, so the image you tested is the image you ship.
COPY ch30_requirements.txt .
RUN pip install --no-cache-dir -r ch30_requirements.txt

COPY ch04_agent.py ch08_sql_tools.py ch08_make_db.py ch30_service.py ./
RUN python ch08_make_db.py && mkdir -p /data && chown app /data
USER app

# The platform checks this; an unhealthy container is replaced automatically.
# (Shell form, so the shell fills in $PORT.)
HEALTHCHECK --interval=30s --timeout=3s CMD python -c \
  "import urllib.request; urllib.request.urlopen('http://127.0.0.1:$PORT/health')"

# Cloud platforms tell the container which port to listen on in $PORT.
CMD ["sh", "-c", "exec uvicorn ch30_service:app --host 0.0.0.0 --port ${PORT} \
     --proxy-headers --no-server-header"]
