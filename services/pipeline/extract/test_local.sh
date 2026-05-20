#!/usr/bin/env bash
set -euo pipefail

IMAGE_NAME="extract:test"
CONTAINER_NAME="extract-local-test"

echo "Building image..."
docker buildx build --platform linux/amd64 --provenance=false -t "$IMAGE_NAME" .

echo "Starting container..."
docker rm -f "$CONTAINER_NAME" 2>/dev/null || true
docker run -d --name "$CONTAINER_NAME" -p 9000:8080 "$IMAGE_NAME"

echo "Waiting for container to be ready..."
sleep 2

echo "Invoking Lambda handler..."
RESPONSE=$(curl -s -X POST "http://localhost:9000/2015-03-31/functions/function/invocations" \
  -d '{}')

echo "Response:"
echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"

echo ""
echo "Cleaning up..."
docker stop "$CONTAINER_NAME" >/dev/null
docker rm "$CONTAINER_NAME" >/dev/null

echo "Done."
