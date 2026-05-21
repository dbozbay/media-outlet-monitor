import json
import logging
from os import getenv

import boto3
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


def configure_logging() -> None:
    """Configure root logging. Call once from the entrypoint."""
    logging.basicConfig(
        level=logging.INFO,
        format="{asctime} - {levelname} - {name} - {message}",
        style="{",
        datefmt="%Y-%m-%d %H:%M",
    )


def get_articles() -> list[dict]:
    """Scan the DynamoDB table and return all articles."""
    dynamodb = boto3.resource("dynamodb", region_name=getenv("AWS_REGION_NAME"))
    table = dynamodb.Table(getenv("DYNAMO_TABLE_NAME"))
    response = table.scan()
    return response.get("Items", [])


def handler(event: dict, context: object) -> dict:
    """AWS Lambda handler for the API Gateway GET /articles route."""
    configure_logging()
    try:
        articles = get_articles()
        logger.info("Returning %d articles", len(articles))
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(articles, default=str),
        }
    except Exception as e:
        logger.exception("Failed to fetch articles")
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": str(e)}),
        }
