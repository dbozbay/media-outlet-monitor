import pytest
from main import (
    clean_source,
    extract_source_article_id,
    generate_article_id,
    prepare_article_for_dynamodb,
)


@pytest.mark.parametrize(
    "url, expected_id",
    [
        ("https://www.bbc.com/news/articles/c9weyz8nk4ro#2", "c9weyz8nk4ro"),
        (
            "https://www.ok.co.uk/celebrity-news/vanessa-feltz-ready-the-one-37161008",
            "37161008",
        ),
        ("https://www.example.com/news/12345", "12345"),
    ],
)
def test_extract_source_article_id(url, expected_id):
    result = extract_source_article_id(url)
    assert result == expected_id


@pytest.mark.parametrize(
    "source, expected",
    [
        ("OK! Magazine", "ok_magazine"),
        ("BBC News", "bbc_news"),
    ],
)
def test_clean_source_removes_special_characters_and_spaces(source, expected):
    result = clean_source(source)
    assert result == expected


def test_generate_article_id_combines_source_and_article_id():
    source = "OK! Magazine"
    url = "https://www.ok.co.uk/celebrity-news/vanessa-feltz-ready-the-one-37161008"
    result = generate_article_id(source, url)
    assert result == "ok_magazine#37161008"


def test_prepare_article_for_dynamodb_returns_expected_dictionary():
    article = {
        "title": "Vanessa Feltz ready for 'The One'",
        "source": "OK! Magazine",
        "link": "https://www.ok.co.uk/celebrity-news/vanessa-feltz-ready-the-one-37161008",
        "summary": "Vanessa Feltz has opened up about her love life.",
        "pub_date": "2026-05-19T13:33:23",
    }
    result = prepare_article_for_dynamodb(article)

    assert result == {
        "article_id": "ok_magazine#37161008",
        "target_name": "unknown",
        "at": "2026-05-19T13:33:23",
        "title": "Vanessa Feltz ready for 'The One'",
        "source": "OK! Magazine",
        "url": "https://www.ok.co.uk/celebrity-news/vanessa-feltz-ready-the-one-37161008",
        "sentiment_score": None,
        "sentiment_label": None,
        "keywords": None,
        "description": "Vanessa Feltz has opened up about her love life.",
    }
