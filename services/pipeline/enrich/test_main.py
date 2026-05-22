from datetime import datetime
from io import BytesIO
from unittest.mock import patch

import pytest
from main import (
    clean_source,
    clean_target_name,
    extract_keywords,
    extract_source_article_id,
    extract_target_names,
    generate_article_id,
    get_sentiment,
    get_text_for_analysis,
    handler,
    prepare_article_for_dynamodb,
    prepare_articles_for_dynamodb,
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


def test_clean_target_name_removes_trailing_quotes():
    result = clean_target_name("Jake Quickenden '")

    assert result == "Jake Quickenden"


def test_extract_target_names_removes_duplicate_cleaned_names():
    text = "Jake Quickenden said Jake Quickenden ' was preparing for a new event."

    result = extract_target_names(text)

    assert "Jake Quickenden" in result
    assert "Jake Quickenden '" not in result
    assert result.count("Jake Quickenden") == 1


def test_get_text_for_analysis_combines_title_summary_and_body():
    article = {
        "title": "Taylor Swift wins award",
        "summary": "Fans praised the singer.",
        "body": "The article body says the performance was excellent.",
    }

    result = get_text_for_analysis(article)

    assert "Taylor Swift wins award" in result
    assert "Fans praised the singer." in result
    assert "performance was excellent" in result


def test_get_sentiment_returns_positive_label():
    score, label = get_sentiment("This is excellent, amazing and wonderful.")

    assert isinstance(score, float)
    assert label == "positive"


def test_get_sentiment_returns_negative_label():
    score, label = get_sentiment("This is terrible, awful and disappointing.")

    assert isinstance(score, float)
    assert label == "negative"


def test_get_sentiment_returns_neutral_label():
    score, label = get_sentiment("The article was published today.")

    assert isinstance(score, float)
    assert label == "neutral"


def test_extract_keywords_returns_list():
    result = extract_keywords("Taylor Swift concert fans praised concert fans")

    assert isinstance(result, list)


def test_extract_keywords_returns_top_keywords_without_duplicates():
    result = extract_keywords("fans fans fans concert concert taylor swift")

    assert result[0] == "fans"
    assert "concert" in result
    assert len(result) == len(set(result))


def test_extract_keywords_limits_to_top_10():
    text = "one two three four five six seven eight nine ten eleven twelve"

    result = extract_keywords(text)

    assert len(result) <= 10


def test_prepare_article_for_dynamodb_returns_records_for_detected_target():
    article = {
        "title": "Taylor Swift wins award",
        "summary": "Taylor Swift was praised by fans.",
        "body": "Taylor Swift gave an excellent performance.",
        "source": "BBC News",
        "link": "https://www.bbc.com/news/articles/c9weyz8nk4ro",
        "pub_date": "2026-05-21T10:00:00",
    }

    result = prepare_article_for_dynamodb(article)

    assert isinstance(result, list)
    assert len(result) >= 1
    assert result[0]["target_name"] == "Taylor Swift"


def test_prepare_article_for_dynamodb_skips_article_with_no_target():
    article = {
        "title": "Weather is sunny today",
        "summary": "The weather is warm and calm.",
        "body": "There are blue skies and light wind.",
        "source": "BBC News",
        "link": "https://www.bbc.com/news/articles/c9weyz8nk4ro",
        "pub_date": "2026-05-21T10:00:00",
    }

    result = prepare_article_for_dynamodb(article)

    assert result == []


def test_prepare_article_for_dynamodb_contains_required_fields():
    article = {
        "title": "Taylor Swift wins award",
        "summary": "Taylor Swift was praised by fans.",
        "body": "Taylor Swift gave an excellent performance.",
        "source": "BBC News",
        "link": "https://www.bbc.com/news/articles/c9weyz8nk4ro",
        "pub_date": "2026-05-21T10:00:00",
    }

    result = prepare_article_for_dynamodb(article)

    assert "article_id" in result[0]
    assert "target_name" in result[0]
    assert "sentiment_score" in result[0]
    assert "keywords" in result[0]


def test_prepare_articles_for_dynamodb_returns_list():
    articles = [
        {
            "title": "Taylor Swift wins award",
            "summary": "Taylor Swift was praised.",
            "body": "Taylor Swift gave an excellent performance.",
            "source": "BBC News",
            "link": "https://www.bbc.com/news/articles/c9weyz8nk4ro",
            "pub_date": "2026-05-21T10:00:00",
        }
    ]

    result = prepare_articles_for_dynamodb(articles)

    assert isinstance(result, list)


def test_prepare_articles_for_dynamodb_flattens_multiple_article_outputs():
    articles = [
        {
            "title": "Taylor Swift and Drake attend event",
            "summary": "Taylor Swift and Drake were both mentioned.",
            "body": "Taylor Swift and Drake appeared together.",
            "source": "BBC News",
            "link": "https://www.bbc.com/news/articles/c9weyz8nk4ro",
            "pub_date": "2026-05-21T10:00:00",
        }
    ]

    result = prepare_articles_for_dynamodb(articles)

    target_names = [record["target_name"] for record in result]

    assert "Taylor Swift" in target_names
    assert "Drake" in target_names


def test_prepare_articles_for_dynamodb_skips_articles_without_targets():
    articles = [
        {
            "title": "Weather is sunny today",
            "summary": "The weather is warm.",
            "body": "There are blue skies.",
            "source": "BBC News",
            "link": "https://www.bbc.com/news/articles/c9weyz8nk4ro",
            "pub_date": "2026-05-21T10:00:00",
        }
    ]

    result = prepare_articles_for_dynamodb(articles)

    assert result == []


def test_handler_loads_articles_from_s3_reference():
    raw_articles = '[{"title": "Taylor Swift wins award", "summary": "Taylor Swift was praised by fans.", "body": "Taylor Swift gave an excellent performance.", "source": "BBC News", "link": "https://www.bbc.com/news/articles/c9weyz8nk4ro", "pub_date": "2026-05-21T10:00:00"}]'
    parsed_articles = [
        {
            "title": "Taylor Swift wins award",
            "summary": "Taylor Swift was praised by fans.",
            "body": "Taylor Swift gave an excellent performance.",
            "source": "BBC News",
            "link": "https://www.bbc.com/news/articles/c9weyz8nk4ro",
            "pub_date": "2026-05-21T10:00:00",
        }
    ]
    ready_articles = [
        {"article_id": "bbc_news#c9weyz8nk4ro", "target_name": "Taylor Swift"}
    ]

    fixed_time = datetime(2026, 5, 22, 14, 30)
    with (
        patch("main.boto3.client") as mock_client_factory,
        patch(
            "main.prepare_articles_for_dynamodb", return_value=ready_articles
        ) as mock_prepare,
        patch.dict("os.environ", {"S3_BUCKET_NAME": "bucket"}),
        patch("main.datetime") as mock_datetime,
    ):
        mock_datetime.now.return_value = fixed_time
        mock_s3_client = mock_client_factory.return_value
        mock_s3_client.get_object.return_value = {
            "Body": BytesIO(raw_articles.encode("utf-8"))
        }

        result = handler({"s3_bucket": "bucket", "s3_key": "extract/articles.json"}, {})

    mock_s3_client.get_object.assert_called_once_with(
        Bucket="bucket", Key="extract/articles.json"
    )
    mock_prepare.assert_called_once_with(parsed_articles)
    assert result == {
        "s3_bucket": "bucket",
        "s3_key": "enriched_articles/2026-05-22T14:30.json",
    }
