# Scripts

Utility scripts for deploying services and running tests. All scripts use `set -euo pipefail` and should be run from the repository root.

## Prerequisites

- **AWS CLI** — configured with appropriate credentials
- **Docker** — with buildx support
- **uv** — for running tests

## Scripts

| Script | Description |
|--------|-------------|
| `deploy-api.sh` | Builds the API service image (linux/amd64), tags it, and pushes to ECR. |
| `deploy-dashboard.sh` | Builds the Streamlit dashboard image and pushes to ECR. |
| `deploy-pipeline.sh` | Builds and pushes all three pipeline stages (extract, enrich, load) to ECR. |
| `run-dashboard.sh` | Builds and runs the dashboard locally on port 8501 using env vars from `.env`. |
| `test-all.sh` | Discovers all services and runs `uv run pytest --cov` in each. |