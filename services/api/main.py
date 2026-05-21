import logging
from os import getenv

import boto3
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from mangum import Mangum
from pydantic import BaseModel, Field
from pydantic.types import PastDatetime

load_dotenv()

logger = logging.getLogger(__name__)

app = FastAPI(title="Articles API")


class Article(BaseModel):
    """Pydantic model representing an article stored in DynamoDB."""

    article_id: str
    title: str
    url: str
    source: str
    description: str
    at: PastDatetime
    target_name: str
    keywords: list[str]
    sentiment_label: str
    sentiment_score: float = Field(..., ge=-1.0, le=1.0)


def get_articles() -> list[dict]:
    """Scan the DynamoDB table and return all articles."""
    dynamodb = boto3.resource("dynamodb", region_name=getenv("AWS_REGION_NAME"))
    table = dynamodb.Table(getenv("DYNAMO_TABLE_NAME"))
    response = table.scan()
    return response.get("Items", [])


def get_articles_by_target(target_name: str, sentiment: str | None = None) -> list[dict]:
    """Scan the DynamoDB table and filter articles by target name (case-insensitive)."""
    dynamodb = boto3.resource("dynamodb", region_name=getenv("AWS_REGION_NAME"))
    table = dynamodb.Table(getenv("DYNAMO_TABLE_NAME"))
    response = table.scan()
    items = [
        item
        for item in response.get("Items", [])
        if item.get("target_name", "").lower() == target_name.lower()
    ]
    if sentiment:
        items = [
            item for item in items
            if item.get("sentiment_label", "").lower() == sentiment.lower()
        ]
    return items


@app.get("/")
async def root():
    return {"message": "🚀 API is running!", "docs": "/docs"}


@app.get("/articles", response_model=list[Article])
async def list_articles():
    """Return all articles."""
    articles = get_articles()
    if not articles:
        raise HTTPException(status_code=404, detail="No articles found")
    return articles


@app.get("/articles/{target_name}", response_model=list[Article])
async def list_articles_by_target(target_name: str, sentiment: str | None = None):
    """Return articles filtered by target name, optionally filtered by sentiment label."""
    articles = get_articles_by_target(target_name, sentiment)
    if not articles:
        detail = f"No articles found for target: {target_name}"
        if sentiment:
            detail += f" with sentiment: {sentiment}"
        raise HTTPException(status_code=404, detail=detail)
    return articles


handler = Mangum(app)
