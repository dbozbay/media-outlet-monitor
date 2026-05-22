# Media Reputation Dashboard

This service provides a Streamlit analytics dashboard for monitoring media coverage of celebrities, brands, and public figures. It queries enriched article records from DynamoDB and visualises article mentions, sentiment trends, keyword themes, source distribution, and recent article cards.

## Features

- Search for a celebrity, brand, or public figure
- View recent article cards with source, timestamp, sentiment, keywords, and article links
- Analyse average daily sentiment
- View sentiment distribution
- Track mention frequency over time
- Identify top keywords and source coverage

## Tech Stack

- Python
- Streamlit
- Pandas
- Altair
- DynamoDB via boto3
- uv package manager
- Ruff for linting/formatting
- Pyrefly for type checking

## Environment Variables

Create a `.env` file in this directory:

```env
DYNAMO_TABLE_NAME=db_name
AWS_REGION_NAME=region_name
```

## Install Dependencies
```
uv sync
```
## Run Locally
```
uv run streamlit run main.py
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