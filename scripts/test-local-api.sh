#!/usr/bin/env bash
set -euo pipefail

IMAGE_NAME="api:test"
CONTAINER_NAME="api-local-test"
SERVICE_DIR="$(dirname "$0")/../services/api"
ENV_FILE="$(dirname "$0")/../.env"

echo "Building image..."
docker buildx build --platform linux/amd64 --provenance=false -t "$IMAGE_NAME" "$SERVICE_DIR"

echo "Starting container..."
docker rm -f "$CONTAINER_NAME" 2>/dev/null || true
docker run -d --name "$CONTAINER_NAME" -p 9000:8080 --env-file "$ENV_FILE" "$IMAGE_NAME"

echo "Waiting for container to be ready..."
sleep 2

echo "=== GET /articles ==="
RESPONSE=$(curl -s -X POST "http://localhost:9000/2015-03-31/functions/function/invocations" \
  -d '{"routeKey": "GET /articles"}')
echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"

echo ""
echo "=== GET /articles/{target_name} (BBC) ==="
RESPONSE=$(curl -s -X POST "http://localhost:9000/2015-03-31/functions/function/invocations" \
  -d '{"routeKey": "GET /articles/{target_name}", "pathParameters": {"target_name": "BBC"}}')
echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"

echo ""
echo "Cleaning up..."
docker stop "$CONTAINER_NAME" >/dev/null
docker rm "$CONTAINER_NAME" >/dev/null

echo "Done."
