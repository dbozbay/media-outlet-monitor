# Load Service

This service loads enriched article records from S3 into DynamoDB for fast querying and dashboard analytics.

## Features

- Loads enriched article JSON from S3
- Inserts enriched records into DynamoDB
- Designed to run as an AWS Lambda container
- Supports downstream analytics dashboards and APIs

## Tech Stack

- Python
- AWS Lambda
- AWS S3
- DynamoDB
- boto3
- python-dotenv
- uv package manager
- Ruff for linting/formatting
- Pyrefly for type checking

## Environment Variables

Create a `.env` file in this directory if running locally:

```env
AWS_REGION_NAME=eu-west-2
DYNAMO_TABLE_NAME=your-dynamodb-table
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
    "s3_key": "enriched_articles/articles.json"
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
docker build -t load-service .
```
## Deployment
```
./scripts/deploy-pipeline.sh
```

Builds and pushes the extract, enrich, and load Docker images to Amazon ECR.

## Run All Tests
```
./scripts/test-all.sh
```

Runs pytest and coverage checks across all services.

Notes

The load service:

- Reads enriched article data from S3
- Loads records into DynamoDB
- Returns the number of successfully loaded articles

DynamoDB is used as the final datastore powering:

- the Streamlit analytics dashboard
- API querying
- sentiment and keyword analytics