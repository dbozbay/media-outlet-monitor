import logging
import re
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


def configure_logging() -> None:
    """Configure root logging. Call once from the entrypoint."""
    logging.basicConfig(
        level=logging.INFO,
        format="{asctime} - {levelname} - {name} - {message}",
        style="{",
        datefmt="%Y-%m-%d %H:%M",
    )


def extract_source_article_id(url: str) -> str:
    """Extracts a unique article ID from the URL based on known patterns for each source."""
    bbc_match = re.search(r"/articles/([a-zA-Z0-9]+)", url)
    if bbc_match:
        return bbc_match.group(1)

    ok_match = re.search(r"-(\d+)$", url)
    if ok_match:
        return ok_match.group(1)

    path = urlparse(url).path
    return path.rstrip("/").split("/")[-1]


def clean_source(source: str) -> str:
    """Cleans the source name to create a consistent source ID."""
    return source.lower().replace("!", "").replace(" ", "_")


def generate_article_id(source: str, url: str) -> str:
    """Generates a unique article ID based on the source and URL."""
    source_id = clean_source(source)
    article_id = extract_source_article_id(url)

    return f"{source_id}#{article_id}"


def prepare_article_for_dynamodb(article: dict) -> dict:
    """Transforms an article dict into a dictionary suitable for DynamoDB."""
    return {
        "article_id": generate_article_id(article["source"], article["link"]),
        "target_name": "unknown",
        "at": article["pub_date"],
        "title": article["title"],
        "source": article["source"],
        "url": article["link"],
        "sentiment_score": None,
        "sentiment_label": None,
        "keywords": None,
        "description": article["summary"],
    }


def prepare_articles_for_dynamodb(articles: list[dict]) -> list[dict]:
    """Transforms a list of article dicts into DynamoDB-ready dictionaries."""
    return [prepare_article_for_dynamodb(article) for article in articles]


def handler(event: list[dict], context: dict) -> list[dict]:
    """AWS Lambda handler that transforms serialized articles into DynamoDB-ready dicts."""
    configure_logging()
    logger.info("Enrich handler received %d articles", len(event))
    ready_articles = prepare_articles_for_dynamodb(event)
    logger.info("Prepared %d articles for DynamoDB", len(ready_articles))
    return ready_articles
