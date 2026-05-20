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


def load_articles_to_dynamodb(articles: list[dict]) -> None:
    """Loads transformed article dictionaries into DynamoDB."""
    dynamodb = boto3.resource("dynamodb", region_name=getenv("AWS_REGION_NAME"))
    table = dynamodb.Table(getenv("DYNAMO_TABLE_NAME"))
    for article in articles:
        table.put_item(Item=article)


def handler(event: list[dict], context: dict) -> list[dict]:
    """AWS Lambda handler for the load step."""
    configure_logging()
    logger.info("Received event with %d articles to load", len(event))
    load_articles_to_dynamodb(event)
    logger.info("Successfully loaded %d articles into DynamoDB", len(event))
    return event
