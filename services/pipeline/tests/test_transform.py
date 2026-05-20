from datetime import datetime
from dataclasses import dataclass

from transform import (
    clean_source,
    extract_source_article_id,
    generate_article_id,
    transform_article_to_dict,
)

@dataclass
class MockArticle:
    title: str
    source: str
    link: str
    summary: str
    pub_date: datetime

def test_extract_source_article_id_for_bbc_url():
    url = "https://www.bbc.com/news/articles/c9weyz8nk4ro#2"

    result = extract_source_article_id(url)

    assert result == "c9weyz8nk4ro"


def test_extract_source_article_id_for_ok_magazine_url():
    url = "https://www.ok.co.uk/celebrity-news/vanessa-feltz-ready-the-one-37161008"

    result = extract_source_article_id(url)

    assert result == "37161008"


def test_clean_source_removes_special_characters_and_spaces():
    source = "OK! Magazine"

    result = clean_source(source)

    assert result == "ok_magazine"


def test_generate_article_id_combines_source_and_article_id():
    source = "OK! Magazine"
    url = "https://www.ok.co.uk/celebrity-news/vanessa-feltz-ready-the-one-37161008"

    result = generate_article_id(source, url)

    assert result == "ok_magazine#37161008"


def test_transform_article_to_dict_returns_expected_dictionary():
    article = MockArticle(
        title="Vanessa Feltz ready for 'The One'",
        source="OK! Magazine",
        link="https://www.ok.co.uk/celebrity-news/vanessa-feltz-ready-the-one-37161008",
        summary="Vanessa Feltz has opened up about her love life.",
        pub_date=datetime(2026, 5, 19, 13, 33, 23),
    )

    result = transform_article_to_dict(article)

    assert result == {
        "article_id": "ok_magazine#37161008",
        "target_name": "",
        "at": "2026-05-19T13:33:23",
        "title": "Vanessa Feltz ready for 'The One'",
        "source": "OK! Magazine",
        "url": "https://www.ok.co.uk/celebrity-news/vanessa-feltz-ready-the-one-37161008",
        "sentiment_score": None,
        "sentiment_label": "",
        "keywords": [],
        "description": "Vanessa Feltz has opened up about her love life.",
    }
