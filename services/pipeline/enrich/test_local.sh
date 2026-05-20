#!/usr/bin/env bash
set -euo pipefail

IMAGE_NAME="enrich:test"
CONTAINER_NAME="enrich-local-test"

echo "Building image..."
docker buildx build --platform linux/amd64 --provenance=false -t "$IMAGE_NAME" .

echo "Starting container..."
docker rm -f "$CONTAINER_NAME" 2>/dev/null || true
docker run -d --name "$CONTAINER_NAME" -p 9001:8080 "$IMAGE_NAME"

echo "Waiting for container to be ready..."
sleep 2

echo "Invoking Lambda handler..."
RESPONSE=$(curl -s -X POST "http://localhost:9001/2015-03-31/functions/function/invocations" \
  -d '[
    {
      "title": "Test Article",
      "source": "BBC News",
      "link": "https://www.bbc.co.uk/news/articles/abc123def",
      "summary": "A test article summary.",
      "pub_date": "2025-05-20T10:00:00"
    }
  ]')

echo "Response:"
echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"

echo ""
echo "Cleaning up..."
docker stop "$CONTAINER_NAME" >/dev/null
docker rm "$CONTAINER_NAME" >/dev/null

echo "Done."
