#!/usr/bin/env bash
# Exercise 30.7: ship the agent API. Run these steps from your workspace folder, on YOUR
# computer (not inside the course container): they need Docker and, for step 3, a cloud CLI.
set -euo pipefail

# ---- 1. Build the production image: only the service's code, pinned versions, non-root user
docker build -f ch30_service.Dockerfile -t agent-api:1 .

# ---- 2. Run it locally exactly as the cloud will, then smoke-test it from the outside.
#         Secrets come from the environment at run time, never from the image.
docker run -d --rm --name agent-api -p 127.0.0.1:8080:8080 \
  -e ANTHROPIC_API_KEY -e AGENT_API_KEYS -e AGENT_MAX_TOKENS=20000 agent-api:1
sleep 3
# The smoke test runs in a second container that shares the service's network, so it
# reaches the service exactly as a client would (the image already has httpx).
docker run --rm --network container:agent-api -v "$PWD:/w:ro" -w /w \
  -e AGENT_API_KEY="${AGENT_API_KEYS%%,*}" agent-api:1 \
  python ch30_smoke_test.py http://127.0.0.1:8080 --chat \
  || { docker logs agent-api; docker stop agent-api; exit 1; }
docker stop agent-api

# ---- 3. Deploy. Example: Google Cloud Run (other managed container hosts work the same way:
#         push the image, set secrets, set a max instance count, get an HTTPS URL).
#   Store the secrets once:
#     printf %s "$ANTHROPIC_API_KEY" | gcloud secrets create anthropic-key --data-file=-
#     printf %s "$AGENT_API_KEYS"    | gcloud secrets create agent-keys    --data-file=-
#   Push the image to Artifact Registry, then:
#     gcloud run deploy agent-api --image "$REGION-docker.pkg.dev/$PROJECT/agents/agent-api:1" \
#       --region "$REGION" --allow-unauthenticated \
#       --set-secrets ANTHROPIC_API_KEY=anthropic-key:latest,AGENT_API_KEYS=agent-keys:latest \
#       --max-instances 1 --concurrency 10 --timeout 300
#   (--allow-unauthenticated lets requests reach the app; the app's own API keys protect it.
#    --max-instances 1 because sessions live in SQLite inside ONE container: see section 30.6.)
#
# ---- 4. Smoke-test the real URL, then look at the logs and set a budget alert.
#     docker run --rm -v "$PWD:/w:ro" -w /w -e AGENT_API_KEY=... agent-api:1 \
#       python ch30_smoke_test.py https://agent-api-xxxx.run.app --chat
#
# ---- 5. Tear it down when you're done, so it can't run up a bill:
#     gcloud run services delete agent-api --region "$REGION"
