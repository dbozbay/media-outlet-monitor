import time

import pytest


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
