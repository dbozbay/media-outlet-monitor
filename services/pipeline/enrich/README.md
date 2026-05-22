# Enrich Service

This service enriches extracted news articles using NLP techniques and prepares them for downstream analytics and storage. It loads raw article data from S3, performs entity extraction, sentiment analysis, and keyword extraction, then uploads the enriched results back to S3.

## Features

- Loads extracted article JSON from S3
- Extracts celebrity, person, and organisation entities using spaCy
- Performs sentiment analysis using NLTK VADER
- Extracts top keywords from article text
- Uploads enriched article records back to S3
- Designed to run as an AWS Lambda container

## Tech Stack

- Python
- AWS Lambda
- AWS S3
- spaCy
- NLTK
- boto3
- uv package manager
- Ruff for linting/formatting
- Pyrefly for type checking

## Environment Variables

Create a `.env` file in this directory if running locally:

```env
AWS_REGION_NAME=eu-west-2
```
## Install Dependencies
```
uv sync
```
## Run Locally
```
uv run python main.py
```
## Example Local Invocation
```python
from main import handler

event = {
    "s3_bucket": "your-bucket-name",
    "s3_key": "extract/articles.json"
}

result = handler(event, {})
print(result)
```
## Run Tests
```
uv run pytest
```
## Run Tests With Coverage
```
uv run pytest --cov
```
## Lint With Ruff
```
uv run ruff check .
```
## Format With Ruff
```
uv run ruff format .
```
## Type Check With Pyrefly
```
uv run pyrefly check
```
## Docker Build
```
docker build -t enrich-service .
```
## Deployment
Deploy Pipeline Services
```
./scripts/deploy-pipeline.sh
```

Builds and pushes the extract, enrich, and load Docker images to Amazon ECR.

## Run All Tests
```
./scripts/test-all.sh
```

Runs pytest and coverage checks across all services.

## Notes

The enrich service:

- Reads extracted article data from S3
- Applies NLP enrichment
- Uploads enriched article JSON back to S3
- Returns the S3 reference for the load stage

The service uses:

- spaCy for entity recognition
- NLTK VADER for sentiment analysis
- Keyword frequency analysis for topic extraction