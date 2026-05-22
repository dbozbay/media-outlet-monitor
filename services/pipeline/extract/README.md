# Extract Service

This service extracts articles from BBC News and OK! Magazine RSS feeds, retrieves the full article body content, and uploads the serialized article data to an S3 bucket for downstream processing.

## Features

- Polls RSS feeds from BBC News and OK! Magazine
- Validates article structure using Pydantic
- Extracts full article body text using BeautifulSoup
- Uploads extracted articles to S3 as JSON
- Designed to run as an AWS Lambda container

## Tech Stack

- Python
- AWS Lambda
- AWS S3
- Feedparser
- Requests
- BeautifulSoup
- Pydantic
- uv package manager
- Ruff for linting/formatting
- Pyrefly for type checking

## Environment Variables

Create a `.env` file in this directory:

```env
S3_BUCKET_NAME=your-bucket-name
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
## Invoke Lambda Handler Locally
```
from main import handler

result = handler({}, {})
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
