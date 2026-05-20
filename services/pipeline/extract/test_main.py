import time
from datetime import datetime
from unittest.mock import patch

import pytest
from pydantic import ValidationError

from main import (
    Article,
    convert_time_struct_to_datetime,
    fetch_feed,
    parse_articles,
    scrape_articles,
)


@pytest.fixture
def sample_article():
    """Provides a sample article dictionary for testing."""
    return {
        "title": "Sample Article",
        "source": "BBC News",
        "link": "https://www.bbc.co.uk/news/sample-article",
        "summary": "This is a sample article for testing.",
        "pub_date": "Wed, 01 Jan 2020 18:00:00 GMT",
    }


@pytest.fixture
def sample_feed_entry():
    """Provides a sample feedparser entry dict."""
    return {
        "title": "Test Article Title",
        "link": "https://www.bbc.co.uk/news/test-123",
        "summary": "A short summary of the article.",
        "published_parsed": time.struct_time((2024, 3, 15, 10, 30, 0, 4, 75, 0)),
    }


@pytest.fixture
def sample_feed_result(sample_feed_entry):
    """Provides a mock feedparser result object."""

    class FeedResult:
        bozo = False
        entries = [sample_feed_entry]

    return FeedResult()


def test_article_valid():
    article = Article(
        title="Hello World",
        source="BBC News",
        link="https://example.com/article",
        summary="A brief summary.",
        pub_date=datetime(2024, 1, 1, 12, 0, 0),
    )
    assert article.title == "Hello World"
    assert article.source == "BBC News"


def test_article_rejects_invalid_source():
    with pytest.raises(ValidationError):
        Article(
            title="Hello",
            source="Unknown Outlet",
            link="https://example.com",
            summary="Summary",
            pub_date=datetime(2024, 1, 1),
        )


def test_article_rejects_future_pub_date():
    with pytest.raises(ValidationError):
        Article(
            title="Hello",
            source="BBC News",
            link="https://example.com",
            summary="Summary",
            pub_date=datetime(2099, 1, 1),
        )


def test_fetch_feed_raises_on_bozo(sample_feed_result):
    sample_feed_result.bozo = True
    sample_feed_result.bozo_exception = Exception("malformed xml")

    with patch("main.feedparser.parse", return_value=sample_feed_result):
        with pytest.raises(ValueError, match="Failed to parse feed"):
            fetch_feed("http://example.com/feed")


def test_fetch_feed_raises_on_empty_entries(sample_feed_result):
    sample_feed_result.entries = []

    with patch("main.feedparser.parse", return_value=sample_feed_result):
        with pytest.raises(ValueError, match="No entries found"):
            fetch_feed("http://example.com/feed")


def test_fetch_feed_returns_entries(sample_feed_result):
    with patch("main.feedparser.parse", return_value=sample_feed_result):
        entries = fetch_feed("http://example.com/feed")
    assert len(entries) == 1
    assert entries[0]["title"] == "Test Article Title"


def test_parse_articles_valid_entries(sample_feed_entry):
    articles = parse_articles([sample_feed_entry], "BBC News")
    assert len(articles) == 1
    assert articles[0].title == "Test Article Title"
    assert articles[0].source == "BBC News"


def test_parse_articles_skips_invalid_entries(sample_feed_entry):
    bad_entry = {
        **sample_feed_entry,
        "published_parsed": (2099, 1, 1, 0, 0, 0, 0, 1, 0),
    }
    articles = parse_articles([sample_feed_entry, bad_entry], "BBC News")
    assert len(articles) == 1


def test_convert_time_struct_to_datetime():
    ts = (2023, 6, 15, 14, 30, 45, 3, 166, 0)
    result = convert_time_struct_to_datetime(ts)
    assert result == datetime(2023, 6, 15, 14, 30, 45)


def test_scrape_articles_aggregates_all_feeds(sample_feed_result):
    with patch("main.feedparser.parse", return_value=sample_feed_result):
        articles = scrape_articles()

    assert len(articles) == 2  # one entry per feed, 2 feeds
    sources = {a.source for a in articles}
    assert "BBC News" in sources
    assert "OK! Magazine" in sources
