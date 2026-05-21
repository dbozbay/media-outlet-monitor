#!/usr/bin/env bash
set -euo pipefail

REGION="eu-west-2"
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
SCRIPT_DIR="$(dirname "$0")"

echo "Logging in to ECR..."
aws ecr get-login-password --region "$REGION" | \
  docker login --username AWS --password-stdin "${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com"

deploy_service() {
  local repo_name="$1"
  local service_dir="$2"
  local image_uri="${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/${repo_name}:latest"

  echo "Building ${repo_name}..."
  docker buildx build --platform linux/amd64 --provenance=false -t "$repo_name" "$service_dir"

  echo "Tagging ${repo_name}..."
  docker tag "${repo_name}:latest" "$image_uri"

  echo "Pushing ${repo_name}..."
  docker push "$image_uri"

  echo "Done: $image_uri"
}

echo "Deploying extract..."
deploy_service "c23-mesopelagic-extract" "$SCRIPT_DIR/../services/pipeline/extract"

echo "Deploying enrich..."
deploy_service "c23-mesopelagic-enrich" "$SCRIPT_DIR/../services/pipeline/enrich"

echo "Deploying load..."
deploy_service "c23-mesopelagic-load" "$SCRIPT_DIR/../services/pipeline/load"

echo "All pipeline services deployed."
