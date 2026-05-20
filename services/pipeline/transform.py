import re
from urllib.parse import urlparse

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


def transform_article_to_dict(article) -> dict:
    """Transforms an article object into a dictionary suitable for the DynamoDB."""
    return {
        "article_id": generate_article_id(article.source, article.link),
        "target_name": "",
        "at": article.pub_date.isoformat(),
        "title": article.title,
        "source": article.source,
        "url": article.link,
        "sentiment_score": None,
        "sentiment_label": "",
        "keywords": [],
        "description": article.summary,
    }

