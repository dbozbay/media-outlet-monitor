#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/services/pipeline"

echo "Deploying extract..."
(cd extract && ./deploy.sh)

echo "Deploying enrich..."
(cd enrich && ./deploy.sh)

echo "Deploying load..."
(cd load && ./deploy.sh)

echo "All pipeline services deployed."