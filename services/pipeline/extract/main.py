"""
BBC UK and OK! RSS News Feed Scraper.
Fetches and parses articles from BBC News and OK! Magazine RSS feeds.
"""

import logging
from datetime import datetime
import requests
from bs4 import BeautifulSoup

import feedparser
from pydantic import BaseModel, ValidationError, field_validator
from pydantic.types import PastDatetime

FEEDS = {
    "BBC News": "http://feeds.bbci.co.uk/news/uk/rss.xml",
    "OK! Magazine": "https://www.ok.co.uk/celebrity-news/?service=rss",
}

logger = logging.getLogger(__name__)


def configure_logging() -> None:
    """Configure root logging. Call once from the entrypoint."""
    logging.basicConfig(
        level=logging.INFO,
        format="{asctime} - {levelname} - {name} - {message}",
        style="{",
        datefmt="%Y-%m-%d %H:%M",
    )


class Article(BaseModel):
    """Represents a news article extracted from an RSS feed."""

    title: str
    source: str
    link: str
    summary: str
    pub_date: PastDatetime
    body: str

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
                body=fetch_article_body(str(entry["link"]).strip()),
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


def fetch_article_body(url: str) -> str:
    """Fetches article page HTML and extracts readable article body text."""
    try:
        response = requests.get(
            url,
            timeout=10,
            headers={"User-Agent": "Mozilla/5.0"},
        )
        response.raise_for_status()
        return extract_body_text(response.text)

    except requests.RequestException as e:
        logger.warning("Failed to fetch article body from %s: %s", url, e)
        return ""


def extract_body_text(html: str) -> str:
    """Extracts readable paragraph text from article HTML."""
    soup = BeautifulSoup(html, "html.parser")

    paragraphs = soup.find_all("p")

    paragraph_text = [
        paragraph.get_text(strip=True)
        for paragraph in paragraphs
        if paragraph.get_text(strip=True)
    ]

    return " ".join(paragraph_text)


def handler(event: dict, context: dict) -> list[dict]:
    """Lambda handler that scrapes articles and returns them as JSON-serializable dicts."""
    configure_logging()
    logger.info("Extract handler invoked")
    articles: list[Article] = scrape_articles()
    logger.info("Returning %d articles", len(articles))
    return [article.model_dump(mode="json") for article in articles]
