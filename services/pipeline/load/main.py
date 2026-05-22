import json
import logging
from os import getenv

import boto3
from dotenv import load_dotenv

load_dotenv()


logger = logging.getLogger(__name__)


def load_articles_from_s3(s3_bucket: str, s3_key: str) -> list[dict]:
    """Loads enriched articles from S3 using the provided bucket and key."""
    s3_client = boto3.client("s3")
    response = s3_client.get_object(Bucket=s3_bucket, Key=s3_key)
    body = response["Body"].read().decode("utf-8")
    return json.loads(body)


def load_articles_to_dynamodb(articles: list[dict]) -> None:
    """Loads transformed article dictionaries into DynamoDB."""
    dynamodb = boto3.resource("dynamodb", region_name=getenv("AWS_REGION_NAME"))
    table = dynamodb.Table(getenv("DYNAMO_TABLE_NAME"))
    for article in articles:
        table.put_item(Item=article)


def handler(event: dict, context: dict) -> dict:
    """AWS Lambda handler for the load step."""
    s3_bucket = event.get("s3_bucket", "")
    s3_key = event.get("s3_key", "")
    articles = load_articles_from_s3(s3_bucket, s3_key)
    logger.info("Received %d articles to load", len(articles))
    load_articles_to_dynamodb(articles)
    logger.info("Successfully loaded %d articles into DynamoDB", len(articles))
    return {"loaded": len(articles)}
