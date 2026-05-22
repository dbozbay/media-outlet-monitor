# Media Outlet Monitor

An automated media monitoring platform that tracks mentions of people and organisations across news outlets. It extracts articles from RSS feeds, enriches them with NLP analysis (sentiment, entities, keywords), and surfaces insights through a REST API and interactive dashboard.

## Architecture

```
EventBridge (scheduled) ─→ Step Functions
                              │
                    ┌─────────┼─────────┐
                    ▼         ▼         ▼
                Extract → Enrich →   Load
                (RSS)    (NLP)    (DynamoDB)
                              │
                    ┌─────────┴─────────┐
                    ▼                   ▼
                   API             Dashboard
                (FastAPI)         (Streamlit)
```

## Services

| Service | Description |
|---------|-------------|
| `services/pipeline/extract` | Scrapes RSS feeds (BBC News, OK! Magazine) and stores raw articles in S3. |
| `services/pipeline/enrich` | Runs spaCy NER, NLTK VADER sentiment, and keyword extraction on raw articles. |
| `services/pipeline/load` | Writes enriched articles to DynamoDB. |
| `services/api` | FastAPI REST API for querying articles by target name and sentiment. |
| `services/dashboard` | Streamlit dashboard with charts for mentions, sentiment trends, and sources. |

## Tech Stack

- **Language:** Python 3.13+
- **NLP:** spaCy, NLTK (VADER)
- **Web:** FastAPI, Streamlit
- **Cloud:** AWS Lambda, DynamoDB, S3, Step Functions, EventBridge, API Gateway, ECS, ECR
- **IaC:** Terraform
- **Dev tools:** uv, pytest, ruff

## Project Structure

```
services/
├── api/              FastAPI server (deployed as Lambda)
├── dashboard/        Streamlit dashboard (deployed on ECS)
└── pipeline/
    ├── extract/      RSS feed scraper
    ├── enrich/       NLP enrichment
    └── load/         DynamoDB loader
infra/                Terraform configurations
scripts/              Deployment and test scripts
```

## Getting Started

### Prerequisites

- Python 3.13+
- [uv](https://docs.astral.sh/uv/)
- Docker with buildx
- AWS CLI (configured for `eu-west-2`)
- Terraform

### Run Tests

```bash
./scripts/test-all.sh
```

### Deploy

```bash
./scripts/deploy-pipeline.sh   # Pipeline lambdas
./scripts/deploy-api.sh        # API lambda
./scripts/deploy-dashboard.sh  # Dashboard container
```

### Run Dashboard Locally

```bash
./scripts/run-dashboard.sh     # Requires .env file at repo root
```