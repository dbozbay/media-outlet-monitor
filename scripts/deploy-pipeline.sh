#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(dirname "$0")"

echo "Deploying extract..."
"$SCRIPT_DIR/deploy-extract.sh"

echo "Deploying enrich..."
"$SCRIPT_DIR/deploy-enrich.sh"

echo "Deploying load..."
"$SCRIPT_DIR/deploy-load.sh"

echo "All pipeline services deployed."
