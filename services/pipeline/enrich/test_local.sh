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
      "title": "Vanessa Feltz ready for The One",
      "source": "BBC News",
      "link": "https://www.ok.co.uk/celebrity-news/vanessa-feltz-ready-the-one-37161008",
      "summary": "Vanessa Feltz has opened up about her love life.",
      "pub_date": "2026-05-19T13:33:23"
    }
  ]')

echo "Response:"
echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"

echo ""
echo "Cleaning up..."
docker stop "$CONTAINER_NAME" >/dev/null
docker rm "$CONTAINER_NAME" >/dev/null

echo "Done."
