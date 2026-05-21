#!/usr/bin/env bash
set -euo pipefail

REPO_NAME="c23-mesopelagic-load"
REGION="eu-west-2"
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
IMAGE_URI="${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/${REPO_NAME}:latest"
SERVICE_DIR="$(dirname "$0")/../services/pipeline/load"

echo "Logging in to ECR..."
aws ecr get-login-password --region "$REGION" | \
  docker login --username AWS --password-stdin "${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com"

echo "Building image..."
docker buildx build --platform linux/amd64 --provenance=false -t "$REPO_NAME" "$SERVICE_DIR"

echo "Tagging image..."
docker tag "${REPO_NAME}:latest" "$IMAGE_URI"

echo "Pushing image..."
docker push "$IMAGE_URI"

echo "Done. Image pushed to: $IMAGE_URI"
