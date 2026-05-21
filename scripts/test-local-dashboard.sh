#!/usr/bin/env bash
set -euo pipefail

IMAGE_NAME="dashboard:test"
CONTAINER_NAME="dashboard-local-test"
SERVICE_DIR="$(dirname "$0")/../services/dashboard"
ENV_FILE="$(dirname "$0")/../.env"

echo "Building image..."
docker buildx build --platform linux/amd64 --provenance=false -t "$IMAGE_NAME" "$SERVICE_DIR"

echo "Starting container..."
docker rm -f "$CONTAINER_NAME" 2>/dev/null || true
docker run --name "$CONTAINER_NAME" -p 8501:8501 --env-file "$ENV_FILE" "$IMAGE_NAME"