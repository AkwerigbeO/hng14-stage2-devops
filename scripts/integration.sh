#!/usr/bin/env bash
set -euo pipefail

TIMEOUT=60
POLL_INTERVAL=2
COMPOSE_FILE="docker-compose.yaml"

cleanup() {
  echo "Tearing down stack..."
  docker compose -f "$COMPOSE_FILE" down -v 2>/dev/null || true
}
trap cleanup EXIT

echo "Starting Docker Compose stack..."
docker compose -f "$COMPOSE_FILE" up -d

echo "Waiting for services to become healthy..."
sleep 15

# Verify frontend is reachable
echo "Checking frontend health..."
curl -sf http://localhost:3000/health > /dev/null || {
  echo "Frontend health check failed!"
  docker compose -f "$COMPOSE_FILE" logs
  exit 1
}

# Submit a job via the frontend
echo "Submitting job..."
JOB_RES=$(curl -s -X POST http://localhost:3000/submit)
echo "Response: $JOB_RES"
JOB_ID=$(echo "$JOB_RES" | python3 -c "import sys,json; print(json.load(sys.stdin).get('job_id',''))" 2>/dev/null || echo "")

if [ -z "$JOB_ID" ]; then
  echo "ERROR: Failed to retrieve job_id from response"
  docker compose -f "$COMPOSE_FILE" logs
  exit 1
fi

echo "Job submitted successfully: $JOB_ID"
echo "Polling for completion (timeout: ${TIMEOUT}s)..."

elapsed=0
while [ $elapsed -lt $TIMEOUT ]; do
  STATUS_RES=$(curl -s "http://localhost:3000/status/$JOB_ID")
  STATUS=$(echo "$STATUS_RES" | python3 -c "import sys,json; print(json.load(sys.stdin).get('status',''))" 2>/dev/null || echo "")
  echo "  [$elapsed s] Status: $STATUS"

  if [ "$STATUS" = "completed" ]; then
    echo "Integration test PASSED — job completed successfully."
    exit 0
  fi

  sleep $POLL_INTERVAL
  elapsed=$((elapsed + POLL_INTERVAL))
done

echo "ERROR: Job did not complete within ${TIMEOUT}s timeout."
docker compose -f "$COMPOSE_FILE" logs
exit 1
