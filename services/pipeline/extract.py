"""
BBC UK and OK! RSS News Feed Scraper.
Fetches and parses articles from BBC News and OK! Magazine RSS feeds.
"""

from datetime import datetime

import feedparser
from logger import configure_logging, get_logger
from pydantic import BaseModel, ValidationError, field_validator
from pydantic.types import PastDatetime

FEEDS = {
    "BBC News": "http://feeds.bbci.co.uk/news/uk/rss.xml",
    "OK! Magazine": "https://www.ok.co.uk/celebrity-news/?service=rss",
}

logger = get_logger(__name__)


class Article(BaseModel):
    """Represents a news article extracted from an RSS feed."""

    title: str
    source: str
    link: str
    summary: str
    pub_date: PastDatetime

    @field_validator("source", mode="before")
    def validate_source(cls, value: str) -> str:
        if value not in FEEDS.keys():
            raise ValueError(f"Invalid source: {value}")
        return value


def scrape_articles() -> list[Article]:
    """Fetches and parses the RSS feed, returning a list of Article objects."""
    articles = []
    for source, url in FEEDS.items():
        logger.info("Fetching feed from %s", url)
        entries = fetch_feed(url)
        logger.info("Fetched %d entries from %s", len(entries), url)
        articles.extend(parse_articles(entries, source))
    logger.info("Scraped %d articles total", len(articles))
    return articles


def fetch_feed(url: str) -> list[dict]:
    """Fetches the RSS feed from the given URL and returns a list of entries."""
    feed = feedparser.parse(url)

    if feed.bozo:
        logger.error("Failed to parse feed from %s: %s", url, feed.bozo_exception)
        raise ValueError(f"Failed to parse feed from {url}: {feed.bozo_exception}")

    if not feed.entries:
        logger.warning("No entries found in feed from %s", url)
        raise ValueError(f"No entries found in feed from {url}")

    return list(feed.entries)


def parse_articles(entries: list[dict], source: str) -> list[Article]:
    """Parses the list of feed entries into Article objects."""
    articles = []
    for entry in entries:
        try:
            pub_time = entry["published_parsed"]

            valid_article = Article(
                title=str(entry["title"]).strip(),
                source=source,
                link=str(entry["link"]).strip(),
                summary=str(entry["summary"]).strip(),
                pub_date=convert_time_struct_to_datetime(pub_time),
            )
            articles.append(valid_article)
        except ValidationError as e:
            logger.warning(
                "Skipping entry due to validation error: '%s'. Error: %s",
                entry.get("title", "N/A"),
                e,
            )
    return articles


def convert_time_struct_to_datetime(time: tuple) -> datetime:
    """Converts a time.struct_time to a datetime object."""
    return datetime(*time[:6])


if __name__ == "__main__":
    configure_logging()
    articles = scrape_articles()
